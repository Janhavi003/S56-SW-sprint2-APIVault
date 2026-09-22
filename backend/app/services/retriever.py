"""
Version-Aware Document Retriever for APIVault.

Performs strict metadata pre-filtering by product_id and version,
calculates relevance scores, and handles insufficient evidence thresholds.
"""

import json
import re
from pathlib import Path
from typing import List, Optional
from app.models.schemas import DocumentChunk, SearchResult


class VersionAwareRetriever:
    """
    Search engine that strictly filters documentation chunks by product and version context.
    """

    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "is", "if", "then", "else", "when",
        "at", "from", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "to", "in", "on",
        "off", "over", "under", "again", "further", "how", "what", "where", "why",
        "should", "can", "could", "would", "do", "does", "did", "doing"
    }

    def __init__(self, chunks: Optional[List[DocumentChunk]] = None, chunk_file_path: Optional[str] = None):
        self.chunks: List[DocumentChunk] = []

        if chunks is not None:
            self.chunks = chunks
        elif chunk_file_path:
            self.load_from_file(chunk_file_path)
        else:
            default_path = Path(__file__).resolve().parent.parent.parent / "data" / "processed_chunks.json"
            if default_path.exists():
                self.load_from_file(str(default_path))

    def load_from_file(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            self.chunks = []
            return

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        self.chunks = [DocumentChunk(**item) for item in raw_data]

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if w not in self.STOPWORDS and len(w) > 1]

    def _calculate_relevance(self, query_tokens: List[str], chunk: DocumentChunk) -> tuple[float, bool]:
        if not query_tokens:
            return 0.0, False

        content_tokens = set(self._tokenize(chunk.content))
        section_tokens = set(self._tokenize(chunk.section_title))
        title_tokens = set(self._tokenize(chunk.document_title))

        matched_content = sum(1 for q in query_tokens if q in content_tokens)
        matched_section = sum(1 for q in query_tokens if q in section_tokens)
        matched_title = sum(1 for q in query_tokens if q in title_tokens)

        content_ratio = matched_content / len(query_tokens)
        section_boost = (matched_section / len(query_tokens)) * 0.4
        title_boost = (matched_title / len(query_tokens)) * 0.2

        raw_score = (content_ratio * 0.5) + section_boost + title_boost
        score = min(1.0, round(raw_score, 4))
        is_exact = matched_section == len(query_tokens) or matched_title == len(query_tokens)

        return score, is_exact

    def search(
        self,
        product_id: str,
        version: str,
        query: str,
        top_k: int = 3,
        min_score_threshold: float = 0.15
    ) -> List[SearchResult]:
        """
        Executes a version-aware search query.

        Strictly filters chunks matching product_id AND version, then scores relevance.
        """
        # Step 1: Strict Metadata Pre-Filtering (Zero Cross-Version Leakage)
        filtered_chunks = [
            c for c in self.chunks
            if c.product_id.strip().lower() == product_id.strip().lower()
            and c.version.strip().lower() == version.strip().lower()
        ]

        if not filtered_chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_results: List[SearchResult] = []
        for chunk in filtered_chunks:
            score, is_exact = self._calculate_relevance(query_tokens, chunk)
            if score >= min_score_threshold:
                scored_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=score,
                        is_exact_match=is_exact
                    )
                )

        # Step 3: Sort by score descending
        scored_results.sort(key=lambda r: r.score, reverse=True)
        return scored_results[:top_k]
