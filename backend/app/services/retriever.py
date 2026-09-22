"""
Version-Aware Retrieval Service for APIVault.

Retrieves documentation chunks strictly isolated by product_id and version,
ranked by deterministic lexical/semantic relevance without external dependencies.
"""

import json
import math
import os
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

from app.models.schemas import DocumentChunk

# Common English stop words to ignore during keyword extraction
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "should", "shouldn't",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "were", "weren't", "what", "when",
    "where", "which", "while", "who", "whom", "why", "with", "won't", "would",
    "wouldn't", "you", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str) -> List[str]:
    """
    Extracts lowercase alphanumeric tokens and code terms from text.
    Handles identifiers (e.g. item_id, v0.100.0, @model_validator).
    """
    # Normalize and extract words/identifiers
    cleaned = text.lower()
    tokens = re.findall(r"[a-z0-9_\.\-/]+", cleaned)
    # Strip leading/trailing punctuation characters from tokens
    stripped_tokens = [t.strip(".-/") for t in tokens if t.strip(".-/")]
    return stripped_tokens


class VersionAwareRetriever:
    """
    Retrieves documentation chunks strictly isolated by product_id and version.

    Enforces:
    1. Strict version isolation before any scoring happens.
    2. Deterministic term frequency and field-weighted relevance scoring.
    3. Source metadata preservation on all returned DocumentChunk objects.
    """

    def __init__(
        self,
        chunks_path: Optional[Union[str, Path]] = None,
        chunks: Optional[List[DocumentChunk]] = None,
    ):
        """
        Initializes the retriever.
        Can receive an explicit list of DocumentChunk objects or load from a JSON file.
        """
        self._chunks: List[DocumentChunk] = []

        if chunks is not None:
            self._chunks = chunks
        else:
            path = chunks_path or self._default_chunks_path()
            self._load_from_path(path)

    @staticmethod
    def _default_chunks_path() -> Path:
        """Resolves the default data/processed_chunks.json path relative to project root."""
        # backend/app/services -> backend -> project_root -> data/processed_chunks.json
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        return project_root / "data" / "processed_chunks.json"

    def _load_from_path(self, path: Union[str, Path]) -> None:
        """Loads and parses chunks from a JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            self._chunks = []
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._chunks = [DocumentChunk(**item) for item in data]

    @property
    def total_chunks(self) -> int:
        """Returns the total number of chunks currently loaded."""
        return len(self._chunks)

    def _score_chunk(
        self,
        chunk: DocumentChunk,
        query_tokens: List[str],
        query_raw: str,
    ) -> float:
        """
        Calculates a deterministic relevance score for a chunk given query tokens.

        Scoring weights:
        - Section title match: 3.0x weight per matching term
        - Document title match: 1.5x weight per matching term
        - Content term frequency: BM25-style saturation: tf / (tf + 1.0)
        - Verbatim query substring in content or section: 5.0x boost
        """
        if not query_tokens:
            return 0.0

        content_lower = chunk.content.lower()
        section_lower = chunk.section_title.lower()
        doc_lower = chunk.document_title.lower()

        content_tokens = tokenize(chunk.content)
        section_tokens = tokenize(chunk.section_title)
        doc_tokens = tokenize(chunk.document_title)

        content_token_set = set(content_tokens)
        section_token_set = set(section_tokens)
        doc_token_set = set(doc_tokens)

        score = 0.0
        matched_terms = 0

        for token in query_tokens:
            token_matched = False

            # Section title match (high relevance)
            if token in section_token_set:
                score += 3.0
                token_matched = True

            # Document title match
            if token in doc_token_set:
                score += 1.5
                token_matched = True

            # Content match with term-frequency saturation
            tf = content_tokens.count(token)
            if tf > 0:
                # Saturation curve: 1 hit -> 0.5, 2 hits -> 0.67, 5 hits -> 0.83
                score += (tf / (tf + 1.0)) * 2.0
                token_matched = True

            if token_matched:
                matched_terms += 1

        # No query keywords matched at all
        if matched_terms == 0:
            return 0.0

        # Exact multi-word substring match bonus
        cleaned_query = query_raw.strip().lower()
        if len(cleaned_query) > 5:
            if cleaned_query in section_lower:
                score += 6.0
            elif cleaned_query in content_lower:
                score += 4.0

        # Match coverage ratio bonus (reward matching a higher percentage of query terms)
        coverage_ratio = matched_terms / len(query_tokens)
        score *= (1.0 + coverage_ratio)

        return score

    def retrieve(
        self,
        product_id: str,
        version: str,
        question: str,
        top_k: int = 3,
        min_score: float = 0.5,
    ) -> List[DocumentChunk]:
        """
        Retrieves top_k relevant chunks for a specific product_id and version.

        Parameters:
        - product_id: Slug identifier (e.g., 'fastapi', 'stripe-api')
        - version: Version string (e.g., 'v0.100.0', 'v2023-10-16')
        - question: Technical question string
        - top_k: Maximum number of chunks to return (default: 3)
        - min_score: Minimum relevance threshold to filter noise (default: 0.5)

        Returns:
        - List of DocumentChunk objects ordered by relevance score descending.
        """
        results_with_scores = self.retrieve_with_scores(
            product_id=product_id,
            version=version,
            question=question,
            top_k=top_k,
            min_score=min_score,
        )
        return [chunk for chunk, _score in results_with_scores]

    def retrieve_with_scores(
        self,
        product_id: str,
        version: str,
        question: str,
        top_k: int = 3,
        min_score: float = 0.5,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieves top_k relevant chunks along with their computed relevance scores.
        FIRST isolates chunks strictly by (product_id, version).
        """
        if not product_id or not version or not question or not question.strip():
            return []

        # 1. STRICT VERSION & PRODUCT ISOLATION FILTERING
        candidate_chunks = [
            chunk for chunk in self._chunks
            if chunk.product_id == product_id and chunk.version == version
        ]

        if not candidate_chunks:
            return []

        # 2. QUERY PREPROCESSING
        raw_tokens = tokenize(question)
        meaningful_tokens = [t for t in raw_tokens if t not in STOP_WORDS]
        query_tokens = meaningful_tokens if meaningful_tokens else raw_tokens

        if not query_tokens:
            return []

        # 3. RELEVANCE SCORING
        scored_chunks: List[Tuple[DocumentChunk, float]] = []
        for chunk in candidate_chunks:
            score = self._score_chunk(chunk, query_tokens, question)
            if score >= min_score:
                scored_chunks.append((chunk, score))

        # 4. RANKING
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # 5. TOP_K SLICING
        return scored_chunks[:top_k]
