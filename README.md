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

Currently in the **Research and Planning** phase.

## Project Structure

```text
frontend/   - User interface
backend/    - Backend and application logic
data/       - Documentation and data resources
docs/       - Project documentation
tests/      - Testing resources