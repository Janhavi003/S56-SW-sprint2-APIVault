"""
Automated unit tests for VersionAwareRetriever.
"""

import sys
import unittest
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import DocumentChunk
from app.services.retriever import VersionAwareRetriever


class TestVersionAwareRetriever(unittest.TestCase):
    def setUp(self):
        self.sample_chunks = [
            DocumentChunk(
                chunk_id="c1",
                product_id="fastapi",
                version="v0.100.0",
                document_title="FastAPI v0.100.0 Routing",
                section_title="Path Parameters",
                content="Data validation performed automatically by Pydantic v1 in FastAPI v0.100.0.",
                token_count=15,
                source_path="data/docs/fastapi/v0.100.0/routing.md"
            ),
            DocumentChunk(
                chunk_id="c2",
                product_id="fastapi",
                version="v0.110.0",
                document_title="FastAPI v0.110.0 Routing",
                section_title="Pydantic v2 Migration Notes",
                content="FastAPI v0.110.0 uses Pydantic v2 for internal schema generation and validation.",
                token_count=16,
                source_path="data/docs/fastapi/v0.110.0/routing.md"
            ),
            DocumentChunk(
                chunk_id="c3",
                product_id="stripe-api",
                version="v2024-04-01",
                document_title="Stripe API Charges",
                section_title="Create a Payment Intent",
                content="In Stripe API version 2024-04-01 create PaymentIntents for customer payments.",
                token_count=14,
                source_path="data/docs/stripe-api/v2024-04-01/charges.md"
            )
        ]
        self.retriever = VersionAwareRetriever(chunks=self.sample_chunks)

    def test_version_isolation(self):
        """Ensure queries for v0.100.0 NEVER leak chunks from v0.110.0"""
        results = self.retriever.search(
            product_id="fastapi",
            version="v0.100.0",
            query="pydantic validation"
        )

        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r.chunk.version, "v0.100.0")
            self.assertNotEqual(r.chunk.version, "v0.110.0")

    def test_product_isolation(self):
        """Ensure queries for fastapi NEVER return stripe-api chunks"""
        results = self.retriever.search(
            product_id="fastapi",
            version="v0.100.0",
            query="payment intent"
        )

        for r in results:
            self.assertEqual(r.chunk.product_id, "fastapi")
            self.assertNotEqual(r.chunk.product_id, "stripe-api")

    def test_insufficient_evidence(self):
        """Ensure completely irrelevant queries return empty results (insufficient evidence)"""
        results = self.retriever.search(
            product_id="fastapi",
            version="v0.100.0",
            query="quantum entanglement thermodynamics",
            min_score_threshold=0.15
        )

        self.assertEqual(len(results), 0)

    def test_relevance_ranking(self):
        """Ensure section heading matches score higher than body text alone"""
        results = self.retriever.search(
            product_id="fastapi",
            version="v0.100.0",
            query="Path Parameters",
            min_score_threshold=0.1
        )

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].chunk.chunk_id, "c1")
        self.assertGreater(results[0].score, 0.3)

    def test_load_from_json_file(self):
        """Ensure retriever loads real chunks from data/processed_chunks.json if available"""
        json_file = Path(__file__).resolve().parent.parent / "data" / "processed_chunks.json"
        if json_file.exists():
            file_retriever = VersionAwareRetriever(chunk_file_path=str(json_file))
            results = file_retriever.search(
                product_id="stripe-api",
                version="v2024-04-01",
                query="PaymentIntents"
            )
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0].chunk.product_id, "stripe-api")
            self.assertEqual(results[0].chunk.version, "v2024-04-01")


if __name__ == "__main__":
    unittest.main()
