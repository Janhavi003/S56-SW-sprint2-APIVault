"""
APIVault Retrieval & E2E Benchmark Suite.

Evaluates:
1. Version-Aware Retrieval Quality (Precision@1, Precision@3, HitRate@1, HitRate@3, MRR).
2. Strict Isolation (0% cross-product / cross-version leakage).
3. Irrelevant Query Rejection (100% true negative rate).
4. Latency performance (Retrieval & End-to-End API Query execution times in milliseconds).

Usage:
    python backend/scripts/benchmark.py
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.schemas import DocumentChunk, GeneratedAnswer
from app.services.generator import AnswerGenerator
from app.services.retriever import VersionAwareRetriever


@dataclass
class BenchmarkItem:
    query_id: str
    category: str  # 'relevant', 'irrelevant', 'cross_version_isolation', 'cross_product_isolation'
    product_id: str
    version: str
    question: str
    expected_source_substring: Optional[str] = None
    expected_section_substring: Optional[str] = None
    forbidden_version: Optional[str] = None
    forbidden_product: Optional[str] = None
    expect_empty: bool = False


# Deterministic Benchmark Dataset
BENCHMARK_DATASET: List[BenchmarkItem] = [
    # --- Category: Relevant Queries (FastAPI v0.100.0) ---
    BenchmarkItem(
        query_id="FA-100-01",
        category="relevant",
        product_id="fastapi",
        version="v0.100.0",
        question="How do I declare path parameters with types in FastAPI?",
        expected_source_substring="routing.md",
        expected_section_substring="Path Parameters with Types",
    ),
    BenchmarkItem(
        query_id="FA-100-02",
        category="relevant",
        product_id="fastapi",
        version="v0.100.0",
        question="How does data validation with Pydantic v1 handle 422 errors?",
        expected_source_substring="routing.md",
        expected_section_substring="Data Validation",
    ),
    BenchmarkItem(
        query_id="FA-100-03",
        category="relevant",
        product_id="fastapi",
        version="v0.100.0",
        question="How do I use yield dependencies and clean-up in FastAPI?",
        expected_source_substring="dependencies.md",
        expected_section_substring="Yield Dependencies and Clean-up",
    ),
    BenchmarkItem(
        query_id="FA-100-04",
        category="relevant",
        product_id="fastapi",
        version="v0.100.0",
        question="How do I declare response_model on route decorators?",
        expected_source_substring="responses.md",
        expected_section_substring="Response Model Declaration",
    ),

    # --- Category: Relevant Queries (FastAPI v0.110.0) ---
    BenchmarkItem(
        query_id="FA-110-01",
        category="relevant",
        product_id="fastapi",
        version="v0.110.0",
        question="How do I declare Annotated dependencies in FastAPI v0.110.0?",
        expected_source_substring="dependencies.md",
        expected_section_substring="Annotated Dependencies",
    ),
    BenchmarkItem(
        query_id="FA-110-02",
        category="relevant",
        product_id="fastapi",
        version="v0.110.0",
        question="What are the migration changes for Pydantic v2 and model_validator?",
        expected_source_substring="routing.md",
        expected_section_substring="Pydantic v2 Migration Notes",
    ),
    BenchmarkItem(
        query_id="FA-110-03",
        category="relevant",
        product_id="fastapi",
        version="v0.110.0",
        question="How do I use the lifespan context manager for startup and shutdown?",
        expected_source_substring="dependencies.md",
        expected_section_substring="Lifespan Events Context Manager",
    ),
    BenchmarkItem(
        query_id="FA-110-04",
        category="relevant",
        product_id="fastapi",
        version="v0.110.0",
        question="How does automatic response model inference work from return type annotations?",
        expected_source_substring="responses.md",
        expected_section_substring="Automatic Response Model Inference",
    ),

    # --- Category: Relevant Queries (Stripe API v2023-10-16) ---
    BenchmarkItem(
        query_id="ST-23-01",
        category="relevant",
        product_id="stripe-api",
        version="v2023-10-16",
        question="What are the required parameters to create a charge with tok_visa?",
        expected_source_substring="charges.md",
        expected_section_substring="Create a Charge",
    ),
    BenchmarkItem(
        query_id="ST-23-02",
        category="relevant",
        product_id="stripe-api",
        version="v2023-10-16",
        question="How do I create a customer with a legacy source token?",
        expected_source_substring="customers.md",
        expected_section_substring="Create a Customer",
    ),
    BenchmarkItem(
        query_id="ST-23-03",
        category="relevant",
        product_id="stripe-api",
        version="v2023-10-16",
        question="How do I create a partial refund for a charge?",
        expected_source_substring="refunds.md",
        expected_section_substring="Create a Refund",
    ),

    # --- Category: Relevant Queries (Stripe API v2024-04-01) ---
    BenchmarkItem(
        query_id="ST-24-01",
        category="relevant",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How do I migrate from Charges to PaymentIntents?",
        expected_source_substring="charges.md",
        expected_section_substring="Migration Notice",
    ),
    BenchmarkItem(
        query_id="ST-24-02",
        category="relevant",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How do I use SetupIntents for saving payment methods without immediate charge?",
        expected_source_substring="customers.md",
        expected_section_substring="SetupIntents for Saving Payment Methods",
    ),
    BenchmarkItem(
        query_id="ST-24-03",
        category="relevant",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How do I search for customers using structured query syntax in Stripe?",
        expected_source_substring="customers.md",
        expected_section_substring="Customer Search API",
    ),
    BenchmarkItem(
        query_id="ST-24-04",
        category="relevant",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How do I submit dispute evidence for chargebacks in Stripe?",
        expected_source_substring="refunds.md",
        expected_section_substring="Dispute Evidence Submission",
    ),

    # --- Category: Irrelevant Queries (Negative Controls) ---
    BenchmarkItem(
        query_id="IRR-01",
        category="irrelevant",
        product_id="fastapi",
        version="v0.100.0",
        question="How do I bake sourdough bread with chocolate chips in an air fryer?",
        expect_empty=True,
    ),
    BenchmarkItem(
        query_id="IRR-02",
        category="irrelevant",
        product_id="stripe-api",
        version="v2023-10-16",
        question="What is the capital of Australia and the weather forecast?",
        expect_empty=True,
    ),
    BenchmarkItem(
        query_id="IRR-03",
        category="irrelevant",
        product_id="fastapi",
        version="v0.110.0",
        question="How do I change the transmission oil on a 2018 Honda Civic?",
        expect_empty=True,
    ),
    BenchmarkItem(
        query_id="IRR-04",
        category="irrelevant",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How to play the Sicilian defense chess opening?",
        expect_empty=True,
    ),

    # --- Category: Cross-Version & Cross-Product Isolation ---
    BenchmarkItem(
        query_id="ISO-VER-01",
        category="cross_version_isolation",
        product_id="fastapi",
        version="v0.100.0",
        question="How to use @model_validator with Pydantic v2 in FastAPI?",
        forbidden_version="v0.110.0",
    ),
    BenchmarkItem(
        query_id="ISO-VER-02",
        category="cross_version_isolation",
        product_id="stripe-api",
        version="v2023-10-16",
        question="How do I use SetupIntents with automatic_payment_methods?",
        forbidden_version="v2024-04-01",
    ),
    BenchmarkItem(
        query_id="ISO-PROD-01",
        category="cross_product_isolation",
        product_id="fastapi",
        version="v0.110.0",
        question="How do I charge a credit card with tok_visa and client_secret?",
        forbidden_product="stripe-api",
    ),
    BenchmarkItem(
        query_id="ISO-PROD-02",
        category="cross_product_isolation",
        product_id="stripe-api",
        version="v2024-04-01",
        question="How do I declare path parameters with Annotated in Python?",
        forbidden_product="fastapi",
    ),
]


def run_benchmark(top_k: int = 3, verbose: bool = True) -> Dict[str, Any]:
    """Runs retrieval and generation benchmark over the dataset."""
    retriever = VersionAwareRetriever()
    generator = AnswerGenerator(retriever=retriever)

    relevant_results = []
    irrelevant_results = []
    isolation_results = []

    retrieval_latencies_ms = []
    generation_latencies_ms = []

    for item in BENCHMARK_DATASET:
        # 1. Measure Retrieval Latency & Output
        t0 = time.perf_counter()
        retrieved_chunks = retriever.retrieve(
            product_id=item.product_id,
            version=item.version,
            question=item.question,
            top_k=top_k,
        )
        retrieval_time_ms = (time.perf_counter() - t0) * 1000.0
        retrieval_latencies_ms.append(retrieval_time_ms)

        # 2. Measure Answer Generation Latency
        t1 = time.perf_counter()
        answer = generator.generate(
            product_id=item.product_id,
            version=item.version,
            question=item.question,
            top_k=top_k,
        )
        generation_time_ms = (time.perf_counter() - t1) * 1000.0
        generation_latencies_ms.append(generation_time_ms)

        # 3. Assess based on Category
        if item.category == "relevant":
            # Check ranks of expected source / section
            hit_k1 = False
            hit_k3 = False
            reciprocal_rank = 0.0
            relevant_count_k3 = 0

            for rank_idx, chunk in enumerate(retrieved_chunks, start=1):
                is_match = False
                if item.expected_source_substring and item.expected_source_substring in chunk.source_path:
                    if not item.expected_section_substring or item.expected_section_substring.lower() in chunk.section_title.lower() or item.expected_section_substring.lower() in chunk.content.lower():
                        is_match = True

                if is_match:
                    relevant_count_k3 += 1
                    if reciprocal_rank == 0.0:
                        reciprocal_rank = 1.0 / rank_idx
                    if rank_idx == 1:
                        hit_k1 = True
                    if rank_idx <= top_k:
                        hit_k3 = True

            precision_k1 = 1.0 if hit_k1 else 0.0
            precision_k3 = relevant_count_k3 / top_k if retrieved_chunks else 0.0

            relevant_results.append({
                "item": item,
                "chunks": retrieved_chunks,
                "hit_k1": hit_k1,
                "hit_k3": hit_k3,
                "precision_k1": precision_k1,
                "precision_k3": precision_k3,
                "mrr": reciprocal_rank,
                "retrieval_ms": retrieval_time_ms,
                "generation_ms": generation_time_ms,
                "status": answer.status,
            })

        elif item.category == "irrelevant":
            passed = len(retrieved_chunks) == 0 and answer.status == "insufficient_documentation"
            irrelevant_results.append({
                "item": item,
                "passed": passed,
                "retrieved_count": len(retrieved_chunks),
                "answer_status": answer.status,
                "retrieval_ms": retrieval_time_ms,
                "generation_ms": generation_time_ms,
            })

        elif "isolation" in item.category:
            leaked = False
            for chunk in retrieved_chunks:
                if item.forbidden_version and chunk.version == item.forbidden_version:
                    leaked = True
                if item.forbidden_product and chunk.product_id == item.forbidden_product:
                    leaked = True
                if chunk.product_id != item.product_id or chunk.version != item.version:
                    leaked = True

            isolation_results.append({
                "item": item,
                "passed": not leaked,
                "leaked": leaked,
                "retrieved_count": len(retrieved_chunks),
                "retrieval_ms": retrieval_time_ms,
                "generation_ms": generation_time_ms,
            })

    # Summary Metrics Calculation
    avg_precision_k1 = sum(r["precision_k1"] for r in relevant_results) / len(relevant_results)
    avg_precision_k3 = sum(r["precision_k3"] for r in relevant_results) / len(relevant_results)
    hit_rate_k1 = sum(1 for r in relevant_results if r["hit_k1"]) / len(relevant_results)
    hit_rate_k3 = sum(1 for r in relevant_results if r["hit_k3"]) / len(relevant_results)
    mrr = sum(r["mrr"] for r in relevant_results) / len(relevant_results)

    irr_rejection_rate = sum(1 for r in irrelevant_results if r["passed"]) / len(irrelevant_results)
    isolation_pass_rate = sum(1 for r in isolation_results if r["passed"]) / len(isolation_results)

    avg_retrieval_ms = sum(retrieval_latencies_ms) / len(retrieval_latencies_ms)
    avg_gen_ms = sum(generation_latencies_ms) / len(generation_latencies_ms)
    sorted_retrieval = sorted(retrieval_latencies_ms)
    p95_retrieval_ms = sorted_retrieval[int(len(sorted_retrieval) * 0.95)]

    summary = {
        "total_queries": len(BENCHMARK_DATASET),
        "relevant_queries": len(relevant_results),
        "irrelevant_queries": len(irrelevant_results),
        "isolation_queries": len(isolation_results),
        "precision_k1": avg_precision_k1,
        "precision_k3": avg_precision_k3,
        "hit_rate_k1": hit_rate_k1,
        "hit_rate_k3": hit_rate_k3,
        "mrr": mrr,
        "irrelevant_rejection_rate": irr_rejection_rate,
        "isolation_pass_rate": isolation_pass_rate,
        "avg_retrieval_latency_ms": avg_retrieval_ms,
        "p95_retrieval_latency_ms": p95_retrieval_ms,
        "avg_generation_latency_ms": avg_gen_ms,
        "relevant_details": relevant_results,
        "irrelevant_details": irrelevant_results,
        "isolation_details": isolation_results,
    }

    if verbose:
        print_benchmark_report(summary)

    return summary


def print_benchmark_report(summary: Dict[str, Any]):
    """Prints a structured benchmark report table to stdout."""
    print("=" * 78)
    print("                      APIVault Retrieval Benchmark Report")
    print("=" * 78)
    print(f"Total Benchmark Queries:     {summary['total_queries']}")
    print(f"  - Relevant Queries:        {summary['relevant_queries']}")
    print(f"  - Irrelevant Queries:      {summary['irrelevant_queries']}")
    print(f"  - Isolation Test Queries:  {summary['isolation_queries']}")
    print("-" * 78)
    print("Retrieval Accuracy & Ranking Metrics:")
    print(f"  * Precision@1:             {summary['precision_k1'] * 100:.1f}%")
    print(f"  * Precision@3:             {summary['precision_k3'] * 100:.1f}%")
    print(f"  * Hit Rate@1:              {summary['hit_rate_k1'] * 100:.1f}%")
    print(f"  * Hit Rate@3:              {summary['hit_rate_k3'] * 100:.1f}%")
    print(f"  * MRR (Mean Reciprocal Rank): {summary['mrr']:.4f}")
    print("-" * 78)
    print("Safety & Filtering Metrics:")
    print(f"  * Irrelevant Rejection:    {summary['irrelevant_rejection_rate'] * 100:.1f}% (True Negative Rate)")
    print(f"  * Version/Product Isolation:{summary['isolation_pass_rate'] * 100:.1f}% (Zero Leakage)")
    print("-" * 78)
    print("Latency Performance:")
    print(f"  * Avg Retrieval Latency:   {summary['avg_retrieval_latency_ms']:.3f} ms")
    print(f"  * p95 Retrieval Latency:   {summary['p95_retrieval_latency_ms']:.3f} ms")
    print(f"  * Avg E2E Generation:      {summary['avg_generation_latency_ms']:.3f} ms")
    print("=" * 78)

    print("\nDetailed Relevant Query Assessment:")
    print(f"{'ID':<11} | {'Product/Ver':<22} | {'Rank 1 Section':<30} | {'MRR':<5} | {'Latency':<8}")
    print("-" * 84)
    for r in summary["relevant_details"]:
        item: BenchmarkItem = r["item"]
        prod_ver = f"{item.product_id} ({item.version})"
        top_section = r["chunks"][0].section_title if r["chunks"] else "None (Miss)"
        if len(top_section) > 28:
            top_section = top_section[:25] + "..."
        print(f"{item.query_id:<11} | {prod_ver:<22} | {top_section:<30} | {r['mrr']:<5.2f} | {r['retrieval_ms']:<6.2f}ms")
    print("-" * 84)


if __name__ == "__main__":
    run_benchmark(top_k=3, verbose=True)
