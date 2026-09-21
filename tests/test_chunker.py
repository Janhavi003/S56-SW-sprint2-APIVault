"""
Unit tests for MarkdownChunker and metadata models.
"""

import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import DocumentChunk, ProductMetadata, VersionMetadata
from app.services.chunker import MarkdownChunker


import unittest


class TestMarkdownChunker(unittest.TestCase):
    def test_product_and_version_metadata_schema(self):
        version = VersionMetadata(version="v1.0.0", doc_dir="docs/fastapi/v1.0.0")
        product = ProductMetadata(
            id="fastapi",
            name="FastAPI",
            description="Web framework",
            versions=[version]
        )
        self.assertEqual(product.id, "fastapi")
        self.assertEqual(len(product.versions), 1)
        self.assertEqual(product.versions[0].version, "v1.0.0")

    def test_markdown_chunker_section_splitting(self):
        sample_markdown = """# FastAPI Routing

## Path Parameters
Path parameters are declared using Python format strings.

## Query Parameters
Query parameters are optional function arguments.
"""
        chunker = MarkdownChunker(max_chunk_words=100)
        chunks = chunker.chunk_markdown(
            text=sample_markdown,
            product_id="fastapi",
            version="v0.100.0",
            source_path="data/docs/fastapi/v0.100.0/routing.md"
        )

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].document_title, "FastAPI Routing")
        self.assertEqual(chunks[0].section_title, "Path Parameters")
        self.assertIn("Path parameters are declared", chunks[0].content)
        self.assertEqual(chunks[0].product_id, "fastapi")
        self.assertEqual(chunks[0].version, "v0.100.0")

        self.assertEqual(chunks[1].section_title, "Query Parameters")
        self.assertIn("Query parameters are optional", chunks[1].content)

    def test_markdown_chunker_sub_chunking(self):
        words = ["word"] * 300
        long_text = "# Title\n\n" + " ".join(words)

        chunker = MarkdownChunker(max_chunk_words=100, overlap_words=20)
        chunks = chunker.chunk_markdown(
            text=long_text,
            product_id="test_prod",
            version="v1.0",
            source_path="test/path.md"
        )

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertEqual(chunk.product_id, "test_prod")
            self.assertEqual(chunk.version, "v1.0")
            self.assertLessEqual(chunk.token_count, 100)

    def test_empty_document_handling(self):
        chunker = MarkdownChunker()
        chunks = chunker.chunk_markdown(
            text="   \n\n  ",
            product_id="test",
            version="v1.0",
            source_path="empty.md"
        )
        self.assertEqual(len(chunks), 0)


if __name__ == "__main__":
    unittest.main()

