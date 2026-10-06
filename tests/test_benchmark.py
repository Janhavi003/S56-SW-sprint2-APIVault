"""
Automated Retrieval Benchmark & Evaluation Tests for APIVault.

Ensures that:
1. Mean Reciprocal Rank (MRR) >= 0.95.
2. Hit Rate@1 >= 0.95 and Hit Rate@3 >= 0.95.
3. 100% Irrelevant Query Rejection (zero hallucination/false positive responses).
4. 100% Strict Version/Product Isolation (zero cross-version/cross-product leakage).
5. Fast Retrieval Latency (average retrieval time < 10ms).
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from scripts.benchmark import run_benchmark


class TestRetrievalBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Execute the deterministic benchmark evaluation once for all assertions."""
        cls.summary = run_benchmark(top_k=3, verbose=False)

    def test_benchmark_hit_rate_and_mrr(self):
        """Verify that relevant queries achieve high retrieval accuracy and MRR >= 0.95."""
        self.assertGreaterEqual(
            self.summary["mrr"],
            0.95,
            f"MRR dropped below 0.95: {self.summary['mrr']:.4f}",
        )
        self.assertGreaterEqual(
            self.summary["hit_rate_k1"],
            0.95,
            f"Hit Rate@1 dropped below 0.95: {self.summary['hit_rate_k1']:.4f}",
        )
        self.assertGreaterEqual(
            self.summary["hit_rate_k3"],
            0.95,
            f"Hit Rate@3 dropped below 0.95: {self.summary['hit_rate_k3']:.4f}",
        )

    def test_benchmark_irrelevant_query_rejection(self):
        """Verify 100% true negative rejection for off-topic/irrelevant questions."""
        self.assertEqual(
            self.summary["irrelevant_rejection_rate"],
            1.0,
            "Irrelevant queries must return 0 chunks with insufficient_documentation status.",
        )

    def test_benchmark_version_isolation(self):
        """Verify 100% strict isolation (zero cross-version or cross-product leakage)."""
        self.assertEqual(
            self.summary["isolation_pass_rate"],
            1.0,
            "Isolation failed: cross-version or cross-product leakage detected in benchmark.",
        )

    def test_benchmark_retrieval_latency(self):
        """Verify retrieval executes well within real-time SLA (< 10 ms average)."""
        self.assertLess(
            self.summary["avg_retrieval_latency_ms"],
            10.0,
            f"Average retrieval latency exceeded SLA: {self.summary['avg_retrieval_latency_ms']:.2f} ms",
        )


if __name__ == "__main__":
    unittest.main()
