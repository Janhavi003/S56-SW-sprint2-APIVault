"""
Data models for Product, Version, Document, and Document Chunk metadata.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class VersionMetadata(BaseModel):
    version: str = Field(..., description="Version identifier, e.g., v0.100.0 or v2024-04-01")
    release_date: Optional[str] = Field(None, description="ISO release date")
    doc_dir: str = Field(..., description="Relative path to documentation directory")


class ProductMetadata(BaseModel):
    id: str = Field(..., description="Unique product slug/identifier")
    name: str = Field(..., description="Human readable product name")
    description: Optional[str] = Field(None, description="Short summary of the product")
    versions: List[VersionMetadata] = Field(default_factory=list, description="Available versions")


class DocumentMetadata(BaseModel):
    doc_id: str = Field(..., description="Unique document ID")
    product_id: str = Field(..., description="Associated product ID")
    version: str = Field(..., description="Associated product version")
    title: str = Field(..., description="Document main title")
    file_path: str = Field(..., description="Relative path to source file")


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk hash/ID")
    product_id: str = Field(..., description="Product slug e.g. fastapi")
    version: str = Field(..., description="Version tag e.g. v0.100.0")
    document_title: str = Field(..., description="Main title of parent document")
    section_title: str = Field(..., description="Heading section name where chunk resides")
    content: str = Field(..., description="Text content of the chunk")
    token_count: int = Field(..., description="Word/token count estimation")
    source_path: str = Field(..., description="Relative file path to source document")


class SearchQuery(BaseModel):
    product_id: str = Field(..., description="Target product identifier")
    version: str = Field(..., description="Target product version tag")
    query: str = Field(..., description="Developer natural language query")
    top_k: int = Field(3, description="Maximum number of chunks to retrieve")
    min_score_threshold: float = Field(0.15, description="Minimum relevance score threshold")


class SearchResult(BaseModel):
    chunk: DocumentChunk = Field(..., description="Matched document chunk")
    score: float = Field(..., description="Normalized relevance score between 0.0 and 1.0")
    is_exact_match: bool = Field(False, description="Flag indicating high-confidence exact section or title match")


class SourceAttribution(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    product_id: str = Field(..., description="Product slug e.g. fastapi")
    version: str = Field(..., description="Version identifier e.g. v0.100.0")
    document_title: str = Field(..., description="Title of parent document")
    section_title: str = Field(..., description="Section title where chunk is located")
    source_path: str = Field(..., description="Relative file path to source document")
    excerpt: Optional[str] = Field(None, description="Brief snippet or excerpt from the chunk content")


class GeneratedAnswer(BaseModel):
    question: str = Field(..., description="Developer natural language question")
    product_id: str = Field(..., description="Target product identifier")
    version: str = Field(..., description="Target product version tag")
    answer: str = Field(..., description="Grounded technical answer generated exclusively from retrieved context")
    status: str = Field("success", description="Status flag: 'success' or 'insufficient_documentation'")
    sources: List[SourceAttribution] = Field(default_factory=list, description="Preserved source attributions used for the answer")
    confidence: float = Field(1.0, description="Confidence score for the answer grounding")


class QueryRequest(BaseModel):
    product_id: str = Field(..., min_length=1, description="Target product identifier e.g. fastapi")
    version: str = Field(..., min_length=1, description="Target product version tag e.g. v0.100.0")
    question: str = Field(..., min_length=1, max_length=1000, description="Technical question")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Maximum number of chunks to retrieve")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="API health status")
    app: str = Field("APIVault", description="Application name")
    version: str = Field("1.0.0", description="API version")



