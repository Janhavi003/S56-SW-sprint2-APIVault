# APIVault

## Version-Aware Technical Documentation Assistant

APIVault is a version-aware technical documentation question-answering system designed to help developers find accurate, verified technical information for specific software products and versions without hallucination or cross-version confusion.

Developers select a product and version, ask a technical question, and receive a grounded answer strictly supported by and cited against the exact documentation source.

---

## Core Problem

Software documentation is frequently fragmented across version-specific docs, release notes, changelogs, and migration guides. This causes developers to:
* Retrieve obsolete or premature syntax for the wrong version (e.g., mixing Pydantic v1 and v2 syntax in FastAPI).
* Encounter hallucinated or merged API behavior across disparate releases.
* Spend excessive time verifying whether an AI answer matches their active SDK/framework release.

---

## Key Differentiator

**Strict Version-Specific Retrieval + Exact Source Attribution**

APIVault is not a generic chatbot. Its primary purpose is to provide deterministic, version-isolated technical answers that developers can verify against exact indexed documentation chunks with zero cross-version or cross-product leakage.

---

## Architecture & Flow

```text
┌────────────────────────────────────────────────────────┐
│                   React + Vite Frontend                 │
│   (Product/Version Selectors, Ask Form, Source View)   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP JSON (POST /api/query)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend API                  │
│                (Validation & Route Handler)            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               VersionAwareRetriever                    │
│   1. Strict pre-filtering by (product_id, version)     │
│   2. Lexical scoring (Section, Title, BM25 saturation) │
│   3. Top-k rank ordering                               │
└───────────────────────────┬────────────────────────────┘
                            │ Retrieved Chunks & Metadata
                            ▼
┌────────────────────────────────────────────────────────┐
│                  AnswerGenerator                       │
│   1. Grounded synthesis strictly from context           │
│   2. Formats citations & confidence score               │
│   3. Insufficient documentation fallback               │
└────────────────────────────────────────────────────────┘
```

---

## Supported Products & Versions

| Product | ID | Registered Versions | Topics Covered |
| :--- | :--- | :--- | :--- |
| **FastAPI** | `fastapi` | `v0.100.0`, `v0.110.0` | Path parameters, Pydantic v1 vs v2, `typing.Annotated`, `Depends()`, `lifespan` context manager, response models |
| **Stripe API** | `stripe-api` | `v2023-10-16`, `v2024-04-01` | Charges API, customer tokens, PaymentIntents migration, SetupIntents, customer search, refunds & disputes |

---

## Major Completed Features

* **Grounded Version-Aware Q&A**: End-to-end question answering strictly constrained to the selected product and version.
* **Exact Source Attribution**: Every response includes source path, document title, section title, and verbatim excerpt.
* **Zero Cross-Version Leakage**: Pre-filtering guarantees that queries for one version never receive context or chunks from another.
* **Persistent Query History**: Browser `localStorage` persistence with automatic hydration, dynamic relative timestamps, click-to-reload, and clear-history support.
* **Markdown Answer Export**: One-click "Copy Answer" and "Copy Source" with full citation formatting and visual feedback.
* **Single-Command Dev Startup**: Unified cross-platform launcher (`python start.py`) running backend and frontend concurrently with process tree cleanup on exit.
* **Automated CI/CD**: GitHub Actions pipeline executing 47 unit & benchmark tests and verifying frontend production builds on every push/PR.

---

## Quick Start

### 1. One-Command Development Startup

Run both the FastAPI backend and Vite frontend concurrently with a single command:

```bash
# Cross-platform (Windows, macOS, Linux)
python start.py
```

* **Frontend UI**: [http://localhost:5173](http://localhost:5173)
* **Backend API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

Press `Ctrl+C` in the terminal to stop both servers simultaneously.

---

### 2. Running Services Individually

```bash
# Start Backend only (Port 8000)
python start.py --backend
# or:
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Start Frontend only (Port 5173)
python start.py --frontend
# or:
cd frontend
npm run dev
```

---

### 3. Running Tests & Data Ingestion

```bash
# Run backend test suite (47 tests including benchmark regression)
python -m unittest discover tests -v

# Run standalone retrieval benchmark evaluation
python backend/scripts/benchmark.py

# Re-run data chunking & ingestion pipeline
python backend/scripts/ingest.py

# Build frontend production bundle
cd frontend && npm run build
```

---

## Backend REST API Endpoints

### 1. Health Check
* **`GET /api/health`**
* **Response**: `{"status": "ok", "app": "APIVault", "version": "1.0.0"}`

### 2. Product & Version Registry
* **`GET /api/products`**
* **Response**: Dynamic list of registered products, descriptions, and supported versions from `data/products.json`.

### 3. Documentation Query
* **`POST /api/query`**
* **Request Body**:
  ```json
  {
    "product_id": "fastapi",
    "version": "v0.110.0",
    "question": "How do lifespan events work in FastAPI?",
    "top_k": 3
  }
  ```
* **Response**:
  ```json
  {
    "status": "success",
    "product_id": "fastapi",
    "version": "v0.110.0",
    "question": "How do lifespan events work in FastAPI?",
    "answer": "...",
    "confidence": 0.85,
    "sources": [
      {
        "chunk_id": "ea91210a9fac1489",
        "document_title": "FastAPI v0.110.0 - Dependency Injection & Lifespan",
        "section_title": "Lifespan Events Context Manager",
        "source_path": "data/docs/fastapi/v0.110.0/dependencies.md",
        "excerpt": "..."
      }
    ]
  }
  ```

---

## Retrieval Benchmark Evaluation

Evaluated across 23 deterministic test cases covering relevant, irrelevant, and cross-version edge cases:

| Metric | Score | SLA Target | Status |
| :--- | :--- | :--- | :--- |
| **Mean Reciprocal Rank (MRR)** | **1.0000** | $\ge 0.95$ | **PASS** |
| **Hit Rate@1** | **100.0%** (15/15) | $\ge 95\%$ | **PASS** |
| **Hit Rate@3** | **100.0%** (15/15) | $\ge 95\%$ | **PASS** |
| **Irrelevant Query Rejection** | **100.0%** (4/4 True Negatives) | $100\%$ | **PASS** |
| **Version/Product Isolation** | **100.0%** (0% Leakage) | $100\%$ | **PASS** |
| **Avg Retrieval Latency** | **0.27 ms** | $< 10.0\text{ ms}$ | **PASS** |
| **Avg E2E Generation Latency** | **0.35 ms** | $< 50.0\text{ ms}$ | **PASS** |

---

## Continuous Integration (CI)

Configured in [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) with parallel validation jobs:
* **`backend-test`**: Sets up Python 3.11 with pip caching, installs `backend/requirements.txt`, and executes all 47 backend tests.
* **`frontend-build`**: Sets up Node.js 20 with npm caching, installs dependencies (`npm ci`), and verifies production compilation (`npm run build`).

---

## Project Structure

```text
.github/
  └── workflows/
      └── ci.yml             # GitHub Actions CI workflow
backend/
  ├── app/
  │   ├── models/schemas.py  # Pydantic data schemas
  │   ├── services/          # Retriever, Generator, Chunker, Validator
  │   └── main.py            # FastAPI HTTP application
  ├── requirements.txt       # Backend Python dependencies
  └── scripts/
      ├── ingest.py          # Markdown chunking & ingestion pipeline
      └── benchmark.py       # Retrieval benchmark evaluation suite
data/
  ├── docs/                  # Version-tagged Markdown documentation
  ├── products.json          # Product & version registry
  └── processed_chunks.json  # Ingested documentation chunks index
docs/
  ├── APIVault_PRD.md        # Product Requirements Document
  └── SPRINT2_DELIVERABLES.md # Sprint 2 Deliverables & Verification Summary
frontend/
  ├── src/                   # React components & UI logic
  ├── package.json           # Frontend dependencies & scripts
  └── vite.config.js         # Vite configuration
tests/                       # Unit, integration, API, and benchmark tests
start.py                     # Unified single-command dev server launcher
start.bat                    # Windows startup script
start.sh                     # Unix/macOS startup script
README.md                    # Project documentation
```
