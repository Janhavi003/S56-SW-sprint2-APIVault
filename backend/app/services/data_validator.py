"""
Validation helpers for the APIVault documentation registry.

The validation layer keeps the product/version registry and documentation
directories aligned before ingestion or retrieval data is generated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DataValidationError(ValueError):
    """Raised when the documentation registry is inconsistent."""


def load_products(products_file: Path) -> list[dict[str, Any]]:
    with products_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list) or not data:
        raise DataValidationError("products.json must contain a non-empty list")

    return data


def validate_product_registry(products_file: Path, data_root: Path) -> list[str]:
    """
    Validate product/version metadata and its documentation directories.

    Returns a list of human-readable validation messages. Raises
    DataValidationError for structural or coverage problems.
    """
    products = load_products(products_file)
    errors: list[str] = []
    product_ids: set[str] = set()

    for product in products:
        product_id = product.get("id")
        name = product.get("name")
        versions = product.get("versions")

        if not product_id or not name or not isinstance(versions, list) or not versions:
            errors.append(f"Invalid product entry: {product!r}")
            continue

        if product_id in product_ids:
            errors.append(f"Duplicate product id: {product_id}")
        product_ids.add(product_id)

        seen_versions: set[str] = set()
        for version in versions:
            version_name = version.get("version")
            doc_dir = version.get("doc_dir")

            if not version_name or not doc_dir:
                errors.append(f"{product_id}: version entry is missing version/doc_dir")
                continue

            if version_name in seen_versions:
                errors.append(f"{product_id}: duplicate version {version_name}")
            seen_versions.add(version_name)

            directory = data_root / doc_dir
            if not directory.is_dir():
                errors.append(
                    f"{product_id}/{version_name}: documentation directory missing: {doc_dir}"
                )
                continue

            markdown_files = list(directory.rglob("*.md"))
            if not markdown_files:
                errors.append(
                    f"{product_id}/{version_name}: no Markdown documentation found"
                )

    if errors:
        raise DataValidationError("\n".join(errors))

    return [
        f"Validated {len(products)} products and "
        f"{sum(len(p['versions']) for p in products)} versions."
    ]


def validate_processed_chunks(
    processed_file: Path, products_file: Path
) -> list[str]:
    """Check that generated chunks only reference registered product/version pairs."""
    with processed_file.open("r", encoding="utf-8") as handle:
        chunks = json.load(handle)
    products = load_products(products_file)

    registered = {
        (product["id"], version["version"])
        for product in products
        for version in product["versions"]
    }

    errors = []
    chunk_ids: set[str] = set()
    project_root = products_file.parent.parent

    for index, chunk in enumerate(chunks):
        pair = (chunk.get("product_id"), chunk.get("version"))
        if pair not in registered:
            errors.append(
                f"Chunk {index} references unregistered product/version: {pair}"
            )

        chunk_id = chunk.get("chunk_id")
        if not chunk_id:
            errors.append(f"Chunk {index} is missing chunk_id")
        elif chunk_id in chunk_ids:
            errors.append(f"Duplicate chunk_id found: {chunk_id}")
        else:
            chunk_ids.add(chunk_id)

        source_path = chunk.get("source_path")
        if not source_path:
            errors.append(f"Chunk {index} is missing source_path")
        elif not (project_root / source_path).is_file():
            errors.append(
                f"Chunk {index} references missing source file: {source_path}"
            )

        content = chunk.get("content")
        token_count = chunk.get("token_count")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"Chunk {index} has empty content")
        elif not isinstance(token_count, int) or token_count <= 0:
            errors.append(f"Chunk {index} has invalid token_count: {token_count}")

    if errors:
        raise DataValidationError("\n".join(errors))

    return [
        f"Validated {len(chunks)} processed chunks with unique IDs, valid source paths, and registered product/version pairs."
    ]
