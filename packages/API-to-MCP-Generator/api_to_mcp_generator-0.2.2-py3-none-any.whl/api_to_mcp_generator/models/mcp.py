"""
MCP (Model Context Protocol) data models.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class MCPParameterType(str, Enum):
    """MCP parameter types."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class MCPParameter(BaseModel):
    """MCP tool or resource parameter."""

    name: str
    type: MCPParameterType
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict[str, Any]] = None
    items: Optional[Dict[str, Any]] = None


class MCPApiMetadata(BaseModel):
    """API metadata for generating HTTP calls from OpenAPI specifications."""

    method: str  # HTTP method: GET, POST, PUT, DELETE, etc.
    path: str  # API path template: /users/{user_id}/profile
    base_url: Optional[str] = None  # Base URL: https://api.example.com
    headers: Optional[Dict[str, str]] = None  # Default headers
    content_type: Optional[str] = None  # Request content type
    response_schema: Optional[Dict[str, Any]] = None  # Expected response schema
    operation_id: Optional[str] = None  # OpenAPI operation ID
    produces: Optional[List[str]] = None  # Response content types
    consumes: Optional[List[str]] = None  # Request content types


class MCPServerInfo(BaseModel):
    """Server information for API calls."""

    base_url: str  # Primary server base URL
    description: Optional[str] = None  # Server description
    variables: Optional[Dict[str, Any]] = None  # Server variables
    authentication: Optional[Dict[str, Any]] = None  # Auth configuration


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str
    description: str
    parameters: List[MCPParameter] = Field(default_factory=list)
    api_metadata: Optional[MCPApiMetadata] = None


class MCPResource(BaseModel):
    """MCP resource definition."""

    name: str
    description: str
    uri: str
    mime_type: Optional[str] = "application/json"
    resource_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")
    api_metadata: Optional[MCPApiMetadata] = None
    uri_template: Optional[str] = None


class MCPServer(BaseModel):
    """Complete MCP server definition."""

    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    tools: List[MCPTool] = Field(default_factory=list)
    resources: List[MCPResource] = Field(default_factory=list)
    server_info: Optional[MCPServerInfo] = None


class MCPConversionResult(BaseModel):
    """Result of OpenAPI to MCP conversion."""

    server: MCPServer
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
