import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.data_validator import (
    DataValidationError,
    validate_processed_chunks,
    validate_product_registry,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class TestDataValidation(unittest.TestCase):
    def test_product_registry_matches_documentation(self):
        messages = validate_product_registry(DATA / "products.json", DATA)
        self.assertIn("Validated 2 products and 4 versions.", messages[0])

    def test_processed_chunks_use_registered_product_versions(self):
        messages = validate_processed_chunks(
            DATA / "processed_chunks.json", DATA / "products.json"
        )
        self.assertEqual(messages, ["Validated 33 processed chunks."])

    def test_registry_rejects_missing_documentation_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            products_file = tmp_path / "products.json"
            products_file.write_text(
                json.dumps(
                    [
                        {
                            "id": "demo",
                            "name": "Demo",
                            "versions": [
                                {
                                    "version": "v1",
                                    "release_date": "2026-01-01",
                                    "doc_dir": "docs/demo/v1",
                                }
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaises(DataValidationError) as ctx:
                validate_product_registry(products_file, tmp_path)
            self.assertIn("documentation directory missing", str(ctx.exception))

    def test_processed_chunks_reject_unknown_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            products_file = tmp_path / "products.json"
            chunks_file = tmp_path / "processed_chunks.json"

            products_file.write_text(
                json.dumps(
                    [
                        {
                            "id": "demo",
                            "name": "Demo",
                            "versions": [
                                {
                                    "version": "v1",
                                    "release_date": "2026-01-01",
                                    "doc_dir": "docs/demo/v1",
                                }
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            chunks_file.write_text(
                json.dumps([{"product_id": "demo", "version": "v2"}]),
                encoding="utf-8",
            )

            with self.assertRaises(DataValidationError) as ctx:
                validate_processed_chunks(chunks_file, products_file)
            self.assertIn("unregistered product/version", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
