"""
API-to-MCP Generator

A Python library to automatically convert any OpenAPI v2/v3 specification 
into a Model Context Protocol (MCP) server, with complete server generation capabilities.
"""

from .parser import load_openapi_spec, get_api_base_url
from .converter import (
    convert_to_mcp,
    convert_to_mcp_enhanced,
    convert_openapi_to_mcp,
    convert_spec_to_mcp,
)
from .filter import parse_filter
from .codegen.server_generator import ServerGenerator
from .resource_generator import ResourceGenerator
from .models.mcp import MCPTool, MCPResource, MCPServer, MCPConversionResult
from .models.server import (
    ServerGenerationRequest,
    ServerGenerationResponse,
    ServerPackage,
)
from .utils.logging import setup_logging, get_logger, LoggerMixin

__version__ = "0.2.0"
__author__ = "Sriram Krishna"
__license__ = "MPL-2.0"

__all__ = [
    "load_openapi_spec",
    "get_api_base_url",
    "convert_to_mcp",
    "convert_to_mcp_enhanced",
    "convert_openapi_to_mcp",
    "convert_spec_to_mcp",
    "parse_filter",
    "ServerGenerator",
    "ResourceGenerator",
    "MCPTool",
    "MCPResource",
    "MCPServer",
    "MCPConversionResult",
    "ServerGenerationRequest",
    "ServerGenerationResponse",
    "ServerPackage",
    "setup_logging",
    "get_logger",
    "LoggerMixin",
]
