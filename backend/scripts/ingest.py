"""
Data Ingestion Script for APIVault.

Traverses product documentation directories, chunks documents while preserving version tags,
and generates data/processed_chunks.json.
"""

import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import ProductMetadata
from app.services.chunker import MarkdownChunker


def run_ingestion():
    project_root = backend_dir.parent
    data_dir = project_root / "data"
    products_file = data_dir / "products.json"
    output_file = data_dir / "processed_chunks.json"

    if not products_file.exists():
        print(f"Error: Products registry not found at {products_file}")
        sys.exit(1)

    with open(products_file, "r", encoding="utf-8") as f:
        products_data = json.load(f)

    products = [ProductMetadata(**p) for p in products_data]
    chunker = MarkdownChunker(max_chunk_words=200, overlap_words=25)
    all_chunks = []

    print("=" * 60)
    print("APIVault Data Ingestion & Chunking Pipeline")
    print("=" * 60)

    for product in products:
        print(f"\n[Product] {product.name} ({product.id})")

        for version_info in product.versions:
            doc_dir = data_dir / version_info.doc_dir.replace("docs/", "docs/")
            version_tag = version_info.version

            print(f"  |-- Version: {version_tag} [Directory: {doc_dir}]")

            if not doc_dir.exists():
                print(f"      [WARNING] Directory does not exist, skipping: {doc_dir}")
                continue

            md_files = list(doc_dir.rglob("*.md"))
            print(f"      [Docs] Found {len(md_files)} markdown files")

            for md_file in md_files:
                rel_path = str(md_file.relative_to(project_root)).replace("\\", "/")
                with open(md_file, "r", encoding="utf-8") as mf:
                    content = mf.read()

                chunks = chunker.chunk_markdown(
                    text=content,
                    product_id=product.id,
                    version=version_tag,
                    source_path=rel_path,
                    default_title=md_file.stem.replace("_", " ").title()
                )

                all_chunks.extend(chunks)
                print(f"      |-- {md_file.name} -> Generated {len(chunks)} chunks")

    # Save output to JSON
    serialized_chunks = [c.model_dump() for c in all_chunks]
    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(serialized_chunks, out_f, indent=2)

    print("\n" + "=" * 60)
    print(f"SUCCESS: Ingestion complete!")
    print(f"Total Chunks Generated: {len(all_chunks)}")
    print(f"Processed Chunks Saved To: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()
