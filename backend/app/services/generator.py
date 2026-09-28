"""
Grounded Answer Generation Service for APIVault.

Consumes retrieved documentation chunks from VersionAwareRetriever and synthesizes
grounded, version-specific technical answers strictly bounded by the retrieved context.
Preserves exact source attribution and provides deterministic fallback for insufficient evidence.
"""

import re
from typing import List, Optional

from app.models.schemas import DocumentChunk, GeneratedAnswer, SourceAttribution
from app.services.retriever import VersionAwareRetriever


class AnswerGenerator:
    """
    Generates technical answers grounded exclusively in retrieved documentation chunks.
    Guarantees:
    1. Zero external hallucination (content is derived strictly from supplied chunks).
    2. Strict preservation of source attribution metadata.
    3. Explicit 'insufficient_documentation' status when evidence is lacking.
    """

    def __init__(self, retriever: Optional[VersionAwareRetriever] = None):
        self.retriever = retriever or VersionAwareRetriever()

    def _extract_excerpt(self, content: str, max_chars: int = 180) -> str:
        """Extracts a clean, single-line text excerpt from a chunk."""
        # Strip markdown headers, code blocks and excessive whitespace
        clean_text = re.sub(r"```[\s\S]*?```", "", content)
        clean_text = re.sub(r"#+\s*", "", clean_text)
        clean_text = " ".join(clean_text.split())
        if len(clean_text) > max_chars:
            return clean_text[:max_chars].rstrip() + "..."
        return clean_text if clean_text else content[:max_chars]

    def _synthesize_answer_body(
        self,
        product_id: str,
        version: str,
        question: str,
        chunks: List[DocumentChunk]
    ) -> str:
        """
        Synthesizes a structured, readable technical answer derived strictly
        from the provided chunks without external knowledge injection.
        """
        answer_parts: List[str] = []

        # Lead with version context
        primary_chunk = chunks[0]
        answer_parts.append(
            f"Based on the official **{primary_chunk.document_title}** for `{product_id}` `{version}`:\n"
        )

        for idx, chunk in enumerate(chunks, 1):
            cleaned_content = chunk.content.strip()
            # If the chunk starts with a header, separate it cleanly
            header_match = re.match(r"^(#{1,4}\s+.*)\n([\s\S]*)", cleaned_content)
            if header_match:
                section_heading = header_match.group(1)
                body = header_match.group(2).strip()
                answer_parts.append(f"### {chunk.section_title}\n{body}\n")
            else:
                answer_parts.append(f"### {chunk.section_title}\n{cleaned_content}\n")

        return "\n".join(answer_parts).strip()

    def generate(
        self,
        product_id: str,
        version: str,
        question: str,
        chunks: Optional[List[DocumentChunk]] = None,
        top_k: int = 3,
        min_score: float = 0.5,
    ) -> GeneratedAnswer:
        """
        Generates a grounded technical answer for a given product, version, and question.

        Parameters:
        - product_id: Product slug (e.g., 'fastapi', 'stripe-api')
        - version: Version string (e.g., 'v0.100.0', 'v2023-10-16')
        - question: Developer question string
        - chunks: Optional pre-retrieved list of DocumentChunk instances. If None, queries self.retriever.
        - top_k: Maximum chunks to retrieve if chunks is None.
        - min_score: Minimum relevance score threshold for retrieval.

        Returns:
        - GeneratedAnswer instance containing the grounded answer, status, and source attributions.
        """
        if not product_id or not version or not question or not question.strip():
            return GeneratedAnswer(
                question=question or "",
                product_id=product_id or "",
                version=version or "",
                answer="Please provide a valid product, version, and technical question.",
                status="insufficient_documentation",
                sources=[],
                confidence=0.0,
            )

        # 1. Retrieve chunks if not explicitly provided
        retrieved_chunks = chunks
        if retrieved_chunks is None:
            retrieved_chunks = self.retriever.retrieve(
                product_id=product_id,
                version=version,
                question=question,
                top_k=top_k,
                min_score=min_score,
            )

        # 2. Handle Insufficient Documentation
        if not retrieved_chunks:
            return GeneratedAnswer(
                question=question,
                product_id=product_id,
                version=version,
                answer=(
                    f"Insufficient documentation available for `{product_id}` `{version}` "
                    f"to reliably answer the question: \"{question}\". "
                    "No matching documentation sections met the relevance threshold."
                ),
                status="insufficient_documentation",
                sources=[],
                confidence=0.0,
            )

        # 3. Grounded Answer Synthesis
        answer_text = self._synthesize_answer_body(
            product_id=product_id,
            version=version,
            question=question,
            chunks=retrieved_chunks,
        )

        # 4. Construct Exact Source Attributions
        sources: List[SourceAttribution] = []
        for chunk in retrieved_chunks:
            sources.append(
                SourceAttribution(
                    chunk_id=chunk.chunk_id,
                    product_id=chunk.product_id,
                    version=chunk.version,
                    document_title=chunk.document_title,
                    section_title=chunk.section_title,
                    source_path=chunk.source_path,
                    excerpt=self._extract_excerpt(chunk.content),
                )
            )

        # Compute confidence based on top chunk availability
        confidence = min(1.0, 0.7 + (0.1 * len(retrieved_chunks)))

        return GeneratedAnswer(
            question=question,
            product_id=product_id,
            version=version,
            answer=answer_text,
            status="success",
            sources=sources,
            confidence=confidence,
        )
