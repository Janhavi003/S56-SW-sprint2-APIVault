# APIVault Documentation Data

This directory contains the documentation corpus and generated retrieval data used by APIVault.

## Current coverage

The MVP corpus currently contains two products with two versions each:

- FastAPI: `v0.100.0`, `v0.110.0`
- Stripe API: `v2023-10-16`, `v2024-04-01`

Each version has its own documentation directory. The product/version registry in
`products.json` is the source of truth for the ingestion pipeline.

## Data flow

```text
data/docs/<product>/<version>/*.md
              |
              v
     products.json registry
              |
              v
    backend/scripts/ingest.py
              |
              v
       MarkdownChunker
              |
              v
     processed_chunks.json
              |
              v
     VersionAwareRetriever
```

The ingestion pipeline preserves product ID, version, document title, section,
content, token count, and source path so retrieved results can be traced back
to the supporting documentation.

## Validation

Before ingestion, the pipeline validates that:

- every registered product has versions;
- product IDs and versions are not duplicated;
- every registered documentation directory exists;
- every registered version contains Markdown documentation.

Generated chunks can also be checked to ensure they only reference registered
product/version pairs.

Run ingestion from the repository root with:

```text
python backend/scripts/ingest.py
```

Run the complete test suite with:

```text
pytest
```

Do not commit API keys, credentials, or other sensitive information to this directory.
