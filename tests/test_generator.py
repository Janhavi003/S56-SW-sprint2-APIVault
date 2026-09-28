"""
Unit and integration tests for AnswerGenerator service.

Verifies:
1. Grounded answer generation using VersionAwareRetriever.
2. Grounded answer generation from explicitly supplied chunks.
3. Strict absence of hallucinated information outside supplied context.
4. Correct preservation of product and version metadata.
5. Exact source attribution retention (document title, section, source path, chunk_id).
6. Proper handling of insufficient documentation cases (empty result, invalid query).
7. Version-specific answer fidelity (FastAPI v0.100.0 vs v0.110.0, Stripe v2023 vs v2024).
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import DocumentChunk, GeneratedAnswer
from app.services.generator import AnswerGenerator
from app.services.retriever import VersionAwareRetriever


class TestAnswerGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize AnswerGenerator with the default retriever."""
        cls.retriever = VersionAwareRetriever()
        cls.generator = AnswerGenerator(retriever=cls.retriever)

    def test_answer_generation_fastapi_v0_100_0(self):
        """Generates grounded answer for FastAPI v0.100.0 and verifies Pydantic v1 context."""
        question = "How does data validation work in FastAPI?"
        result: GeneratedAnswer = self.generator.generate(
            product_id="fastapi",
            version="v0.100.0",
            question=question,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.product_id, "fastapi")
        self.assertEqual(result.version, "v0.100.0")
        self.assertEqual(result.question, question)
        self.assertGreaterEqual(result.confidence, 0.7)

        # Grounding check: should contain Pydantic v1 info, must NOT mention Pydantic v2
        self.assertIn("Pydantic v1", result.answer)
        self.assertNotIn("Pydantic v2", result.answer)

        # Source check
        self.assertGreater(len(result.sources), 0)
        source = result.sources[0]
        self.assertEqual(source.product_id, "fastapi")
        self.assertEqual(source.version, "v0.100.0")
        self.assertTrue(source.source_path.endswith("routing.md"))
        self.assertTrue(source.chunk_id)
        self.assertTrue(source.section_title)
        self.assertTrue(source.document_title)
        self.assertTrue(source.excerpt)

    def test_answer_generation_fastapi_v0_110_0(self):
        """Generates grounded answer for FastAPI v0.110.0 and verifies Pydantic v2 / Annotated context."""
        question = "What are the changes for Pydantic v2 and model_validator?"
        result: GeneratedAnswer = self.generator.generate(
            product_id="fastapi",
            version="v0.110.0",
            question=question,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.product_id, "fastapi")
        self.assertEqual(result.version, "v0.110.0")
        self.assertIn("Pydantic v2", result.answer)
        self.assertIn("@model_validator", result.answer)
        self.assertNotIn("Pydantic v1", result.answer)

        self.assertGreater(len(result.sources), 0)
        self.assertEqual(result.sources[0].version, "v0.110.0")

    def test_answer_generation_stripe_v2023_10_16(self):
        """Generates grounded answer for Stripe API v2023-10-16 Charges endpoint."""
        question = "How do I create a charge?"
        result: GeneratedAnswer = self.generator.generate(
            product_id="stripe-api",
            version="v2023-10-16",
            question=question,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.product_id, "stripe-api")
        self.assertEqual(result.version, "v2023-10-16")
        self.assertIn("/v1/charges", result.answer)
        self.assertIn("tok_visa", result.answer)

    def test_answer_generation_stripe_v2024_04_01(self):
        """Generates grounded answer for Stripe API v2024-04-01 PaymentIntents migration."""
        question = "How do I create a payment intent?"
        result: GeneratedAnswer = self.generator.generate(
            product_id="stripe-api",
            version="v2024-04-01",
            question=question,
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.product_id, "stripe-api")
        self.assertEqual(result.version, "v2024-04-01")
        self.assertIn("/v1/payment_intents", result.answer)
        self.assertIn("automatic_payment_methods", result.answer)

    def test_insufficient_documentation_for_irrelevant_question(self):
        """Irrelevant query returns an explicit insufficient_documentation status and empty sources."""
        question = "How do I make Italian sourdough pizza with olives?"
        result: GeneratedAnswer = self.generator.generate(
            product_id="fastapi",
            version="v0.100.0",
            question=question,
        )

        self.assertEqual(result.status, "insufficient_documentation")
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.sources, [])
        self.assertIn("Insufficient documentation available", result.answer)

    def test_insufficient_documentation_on_empty_input(self):
        """Empty input fields return an explicit insufficient_documentation result."""
        res_empty_q = self.generator.generate(product_id="fastapi", version="v0.100.0", question="")
        self.assertEqual(res_empty_q.status, "insufficient_documentation")
        self.assertEqual(res_empty_q.sources, [])

        res_empty_p = self.generator.generate(product_id="", version="v0.100.0", question="test")
        self.assertEqual(res_empty_p.status, "insufficient_documentation")

    def test_grounded_answer_from_supplied_chunks(self):
        """Verifies zero external hallucination by passing a synthetic isolated chunk."""
        custom_chunk = DocumentChunk(
            chunk_id="synthetic-abc-123",
            product_id="mock-db",
            version="v9.0",
            document_title="MockDB Manual",
            section_title="Port Configuration",
            content="MockDB listens by default on TCP port 9876 using protocol XYZ.",
            token_count=11,
            source_path="data/docs/mock-db/manual.md",
        )

        result = self.generator.generate(
            product_id="mock-db",
            version="v9.0",
            question="What port does MockDB use?",
            chunks=[custom_chunk],
        )

        self.assertEqual(result.status, "success")
        self.assertIn("port 9876", result.answer)
        self.assertIn("protocol XYZ", result.answer)
        self.assertIn("MockDB Manual", result.answer)
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].chunk_id, "synthetic-abc-123")
        self.assertEqual(result.sources[0].source_path, "data/docs/mock-db/manual.md")

    def test_source_attribution_metadata_preservation(self):
        """All source metadata fields from retrieved chunks must be preserved accurately in GeneratedAnswer."""
        result = self.generator.generate(
            product_id="stripe-api",
            version="v2024-04-01",
            question="What is the response when creating a payment intent?",
            top_k=2,
        )

        self.assertEqual(result.status, "success")
        self.assertGreater(len(result.sources), 0)
        for src in result.sources:
            self.assertTrue(src.chunk_id)
            self.assertEqual(src.product_id, "stripe-api")
            self.assertEqual(src.version, "v2024-04-01")
            self.assertTrue(src.document_title)
            self.assertTrue(src.section_title)
            self.assertTrue(src.source_path)
            self.assertTrue(src.excerpt)


if __name__ == "__main__":
    unittest.main()
