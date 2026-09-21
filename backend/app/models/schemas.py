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
