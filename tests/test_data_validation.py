import json
from pathlib import Path

import pytest

from app.services.data_validator import (
    DataValidationError,
    validate_processed_chunks,
    validate_product_registry,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_product_registry_matches_documentation():
    messages = validate_product_registry(DATA / "products.json", DATA)
    assert "Validated 2 products and 4 versions." in messages


def test_processed_chunks_use_registered_product_versions():
    messages = validate_processed_chunks(
        DATA / "processed_chunks.json", DATA / "products.json"
    )
    assert messages == ["Validated 10 processed chunks."]


def test_registry_rejects_missing_documentation_directory(tmp_path):
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

    with pytest.raises(DataValidationError, match="documentation directory missing"):
        validate_product_registry(products_file, tmp_path)


def test_processed_chunks_reject_unknown_version(tmp_path):
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

    with pytest.raises(DataValidationError, match="unregistered product/version"):
        validate_processed_chunks(chunks_file, products_file)
