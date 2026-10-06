# APIVault

## Version-Aware Technical Documentation Assistant

APIVault is a version-aware documentation question-answering system designed to help developers find accurate technical information for a specific software product and version.

Developers can select a product and version, ask a technical question, and receive an answer supported by the relevant documentation source.

## Core Problem

Software documentation is often distributed across:

- API references
- Version-specific documentation
- Migration guides
- Changelogs
- Release notes
- Technical guides

This can cause developers to:

- Find information for the wrong version
- Mix information from different versions
- Spend time searching multiple documentation sources
- Make integration mistakes
- Have difficulty verifying whether an answer is correct

## Core Solution

APIVault focuses on:

**Product + Version → Question → Retrieval → Answer → Exact Source**

The system should retrieve documentation relevant to the selected product and version, provide a grounded answer, and show the source used to support that answer.

## Key Differentiator

**Version-Specific Answers + Exact Source Attribution**

APIVault is not intended to be a generic chatbot. Its primary purpose is to provide version-aware technical answers that developers can verify against the original documentation.

## MVP

The initial MVP will allow a developer to:

1. Select a product
2. Select a version
3. Ask a technical question
4. Retrieve relevant version-specific documentation
5. Receive a grounded answer
6. Inspect the supporting source

## Project Status

MVP complete with grounded version-aware retrieval and exact source attribution.

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

If you prefer running services in separate terminals:

```bash
# Start Backend only (Port 8000)
python start.py --backend
# or:
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Start Frontend only (Port 5173)
python start.py --frontend
# or:
cd frontend
npm run dev
```

---

### 3. Running Tests & Data Ingestion

```bash
# Run backend test suite
python -m unittest discover tests -v

# Re-run data chunking & ingestion pipeline
python backend/scripts/ingest.py

# Build frontend production bundle
cd frontend && npm run build
```

---

## Project Structure

```text
frontend/   - React + Vite user interface
backend/    - FastAPI application & RAG services (Retriever, Generator, Chunker)
data/       - Version-tagged documentation Markdown files & processed chunks
docs/       - Architecture & project specifications
tests/      - Unit and integration test suite
start.py    - Unified single-command development launcher
```