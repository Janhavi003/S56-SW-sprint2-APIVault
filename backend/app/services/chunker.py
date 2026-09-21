"""
Markdown Document Chunker service for APIVault.

Splits markdown documentation into semantic chunks, preserving heading titles,
version tags, product IDs, and document paths.
"""

import hashlib
import re
from typing import List
from app.models.schemas import DocumentChunk


class MarkdownChunker:
    """
    Splits markdown files into structured chunks tagged with product and version metadata.
    """

    def __init__(self, max_chunk_words: int = 250, overlap_words: int = 30):
        self.max_chunk_words = max_chunk_words
        self.overlap_words = overlap_words

    def _generate_chunk_id(self, product_id: str, version: str, content: str, index: int) -> str:
        raw_key = f"{product_id}:{version}:{index}:{content[:60]}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def _estimate_token_count(self, text: str) -> int:
        return len(text.split())

    def chunk_markdown(
        self,
        text: str,
        product_id: str,
        version: str,
        source_path: str,
        default_title: str = "Documentation"
    ) -> List[DocumentChunk]:
        """
        Processes raw markdown string and returns a list of DocumentChunk instances.
        """
        lines = text.splitlines()
        chunks: List[DocumentChunk] = []

        document_title = default_title
        current_section = "Overview"
        current_buffer: List[str] = []

        def flush_buffer(doc_title: str, sec_title: str, buffer_lines: List[str]):
            content = "\n".join(buffer_lines).strip()
            if not content:
                return

            words = content.split()
            if len(words) <= self.max_chunk_words:
                chunk_id = self._generate_chunk_id(product_id, version, content, len(chunks))
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        product_id=product_id,
                        version=version,
                        document_title=doc_title,
                        section_title=sec_title,
                        content=content,
                        token_count=len(words),
                        source_path=source_path,
                    )
                )
            else:
                # Sub-chunking for longer sections
                start = 0
                step = self.max_chunk_words - self.overlap_words
                while start < len(words):
                    sub_words = words[start : start + self.max_chunk_words]
                    sub_content = " ".join(sub_words)
                    chunk_id = self._generate_chunk_id(product_id, version, sub_content, len(chunks))
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            product_id=product_id,
                            version=version,
                            document_title=doc_title,
                            section_title=f"{sec_title} (Part {len(chunks) + 1})",
                            content=sub_content,
                            token_count=len(sub_words),
                            source_path=source_path,
                        )
                    )
                    start += step

        for line in lines:
            header_match = re.match(r"^(#{1,3})\s+(.*)$", line.strip())
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                if level == 1:
                    document_title = title
                    # Also set section to title if starting fresh
                    if not current_buffer:
                        current_section = title
                    else:
                        flush_buffer(document_title, current_section, current_buffer)
                        current_buffer = []
                        current_section = title
                else:
                    flush_buffer(document_title, current_section, current_buffer)
                    current_buffer = [line]
                    current_section = title
            else:
                current_buffer.append(line)

        flush_buffer(document_title, current_section, current_buffer)
        return chunks
