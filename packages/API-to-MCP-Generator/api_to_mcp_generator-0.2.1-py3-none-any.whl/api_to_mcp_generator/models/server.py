"""
Server generation data models.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ServerGenerationRequest(BaseModel):
    """Request model for MCP server generation."""

    server_name: str
    server_description: Optional[str] = None
    package_name: Optional[str] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    base_url: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None


class ServerFile(BaseModel):
    """Generated server file."""

    path: str
    content: str
    description: Optional[str] = None


class ServerPackage(BaseModel):
    """Generated server package structure."""

    name: str
    version: str
    files: List[ServerFile] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    entry_point: Optional[str] = None


class ServerGenerationResponse(BaseModel):
    """Response model for server generation."""

    package: ServerPackage
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
