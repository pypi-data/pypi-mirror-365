"""
Server code generation using Python AST.
"""

import ast
import re
import textwrap
from typing import Dict, List, Optional, Any
from ..models.server import (
    ServerGenerationRequest,
    ServerGenerationResponse,
    ServerPackage,
    ServerFile,
)
from ..models.mcp import MCPTool, MCPResource
from ..utils.logging import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)

logger = get_logger(__name__)


def sanitize_python_identifier(name: str) -> str:
    """Sanitize a string to be a valid Python identifier."""
    # Remove or replace invalid characters
    # Keep only letters, numbers, and underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name)

    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"

    # Ensure it's not empty
    if not sanitized:
        sanitized = "Server"

    return sanitized


class ServerGenerator:
    """Generates complete MCP server implementations from MCP definitions."""

    def __init__(self):
        logger.debug("Initializing ServerGenerator")
        self.template_generator = TemplateGenerator()

    def generate_server(
        self, request: ServerGenerationRequest
    ) -> ServerGenerationResponse:
        """Generate a complete MCP server package."""
        log_operation_start(
            "generate_server",
            {
                "server_name": request.server_name,
                "tools_count": len(request.tools),
                "resources_count": len(request.resources),
                "has_auth": bool(request.authentication),
            },
            logger,
        )

        try:
            files = []
            dependencies = [
                "mcp>=0.5.0",
                "pydantic>=2.0.0",
                "httpx>=0.24.0",
                "structlog>=21.1.0",
            ]

            # Generate main server file
            logger.debug("Generating main server file")
            server_file = self._generate_server_file(request)
            files.append(server_file)

            # Generate tool implementations
            logger.debug("Generating tool implementations", count=len(request.tools))
            tool_files = self._generate_tool_files(request.tools, request.base_url)
            files.extend(tool_files)

            # Generate resource implementations
            logger.debug(
                "Generating resource implementations", count=len(request.resources)
            )
            resource_files = self._generate_resource_files(
                request.resources, request.base_url
            )
            files.extend(resource_files)

            # Generate configuration file
            logger.debug("Generating configuration file")
            config_file = self._generate_config_file(request)
            files.append(config_file)

            # Generate requirements.txt
            requirements_file = ServerFile(
                path="requirements.txt",
                content="\n".join(dependencies),
                description="Python dependencies",
            )
            files.append(requirements_file)

            # Generate setup files
            logger.debug("Generating setup files")
            setup_files = self._generate_setup_files(request)
            files.extend(setup_files)

            package = ServerPackage(
                name=request.package_name
                or request.server_name.lower().replace(" ", "_"),
                version=request.version,
                files=files,
                dependencies=dependencies,
                entry_point=f"{request.server_name.lower().replace(' ', '_')}.server:main",
            )

            log_operation_success(
                "generate_server",
                {
                    "package_name": package.name,
                    "generated_files": len(files),
                    "tools_count": len(request.tools),
                    "resources_count": len(request.resources),
                },
                logger,
            )

            return ServerGenerationResponse(
                package=package,
                metadata={
                    "generated_files": len(files),
                    "tools_count": len(request.tools),
                    "resources_count": len(request.resources),
                },
            )

        except Exception as e:
            log_operation_error(
                "generate_server",
                e,
                {
                    "server_name": request.server_name,
                    "tools_count": len(request.tools),
                    "resources_count": len(request.resources),
                },
                logger,
            )

            return ServerGenerationResponse(
                package=ServerPackage(name="", version=""),
                errors=[f"Server generation failed: {str(e)}"],
            )

    def _generate_server_file(self, request: ServerGenerationRequest) -> ServerFile:
        """Generate the main MCP server file."""
        server_name = request.server_name.lower().replace(" ", "_")
        # Create a safe Python class name
        class_name = (
            sanitize_python_identifier(request.server_name.replace(" ", "")) + "Server"
        )

        content = f'''"""
{request.server_name} MCP Server
{request.server_description or f"MCP server for {request.server_name}"}

Generated by API-to-MCP-Generator
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, TextContent
import structlog
import httpx

from .config import ServerConfig
from .tools import *
from .resources import *

# Configure logging
logger = structlog.get_logger(__name__)

class {class_name}:
    """Main MCP server class."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server("{server_name}")
        self.client = httpx.AsyncClient()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP handlers."""
        # Register tool handlers
{self._generate_tool_registrations(request.tools)}
        
        # Register resource handlers  
{self._generate_resource_registrations(request.resources)}
    
    async def run(self):
        """Run the MCP server."""
        try:
            async with self.server.run_stdio() as streams:
                await self.server.run(
                    streams[0], streams[1], InitializationOptions()
                )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            await self.client.aclose()

def main():
    """Main entry point."""
    config = ServerConfig()
    server = {class_name}(config)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
'''

        return ServerFile(
            path="server.py",
            content=content,
            description="Main MCP server implementation",
        )

    def _generate_tool_registrations(self, tools: List[Dict[str, Any]]) -> str:
        """Generate tool registration code."""
        if not tools:
            return "        # No tools to register"

        registrations = []
        for tool in tools:
            tool_name = tool.get("name", "unknown_tool")
            registrations.append(
                f"        self.server.register_tool('{tool_name}', {tool_name}_handler)"
            )

        return "\n".join(registrations)

    def _generate_resource_registrations(self, resources: List[Dict[str, Any]]) -> str:
        """Generate resource registration code."""
        if not resources:
            return "        # No resources to register"

        registrations = []
        for resource in resources:
            resource_name = resource.get("name", "unknown_resource")
            clean_name = resource_name.lower().replace(" ", "_")
            registrations.append(
                f"        self.server.register_resource('{resource_name}', {clean_name}_handler)"
            )

        return "\n".join(registrations)

    def _generate_tool_files(
        self, tools: List[Dict[str, Any]], base_url: Optional[str]
    ) -> List[ServerFile]:
        """Generate tool implementation files."""
        if not tools:
            return [
                ServerFile(
                    path="tools/__init__.py",
                    content="# No tools generated\n",
                    description="Empty tools module",
                )
            ]

        files = []

        # Generate tools __init__.py
        tool_imports = []
        for tool in tools:
            tool_name = tool.get("name", "unknown_tool")
            tool_imports.append(f"from .{tool_name} import {tool_name}_handler")

        init_content = f'''"""
Tool implementations for the MCP server.
"""
{chr(10).join(tool_imports)}

__all__ = [
{chr(10).join([f'    "{tool.get("name", "unknown_tool")}_handler",' for tool in tools])}
]
'''

        files.append(
            ServerFile(
                path="tools/__init__.py",
                content=init_content,
                description="Tools module initialization",
            )
        )

        # Generate individual tool files
        for tool in tools:
            tool_file = self._generate_tool_file(tool, base_url)
            files.append(tool_file)

        return files

    def _generate_tool_file(
        self, tool: Dict[str, Any], base_url: Optional[str]
    ) -> ServerFile:
        """Generate individual tool implementation."""
        tool_name = tool.get("name", "unknown_tool")
        description = tool.get("description", f"Tool: {tool_name}")

        # Extract API metadata
        api_info = tool.get("api_metadata", {})
        method = api_info.get("method", "GET").upper()
        path = api_info.get("path", "/")
        url = f"{base_url or 'https://api.example.com'}{path}"

        content = f'''"""
{tool_name} tool implementation.
"""
import json
from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)

async def {tool_name}_handler(arguments: Dict[str, Any]) -> str:
    """
    {description}
    
    Args:
        arguments: Tool arguments from MCP client
        
    Returns:
        JSON string with the API response
    """
    try:
        async with httpx.AsyncClient() as client:
            # Prepare request parameters
            url = "{url}"
            method = "{method}"
            
            # Handle path parameters
            for key, value in arguments.items():
                if "{{" + key + "}}" in url:
                    url = url.replace("{{" + key + "}}", str(value))
            
            # Prepare request data
            request_data = {{}}
            query_params = {{}}
            
            for key, value in arguments.items():
                if key not in url:  # Not a path parameter
                    if method in ["GET", "DELETE"]:
                        query_params[key] = value
                    else:
                        request_data[key] = value
            
            # Make API request
            if method == "GET":
                response = await client.get(url, params=query_params)
            elif method == "POST":
                response = await client.post(url, json=request_data, params=query_params)
            elif method == "PUT":
                response = await client.put(url, json=request_data, params=query_params)
            elif method == "DELETE":
                response = await client.delete(url, params=query_params)
            else:
                raise ValueError(f"Unsupported HTTP method: {{method}}")
            
            response.raise_for_status()
            
            # Return response
            result = {{
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }}
            
            return json.dumps(result, indent=2)
            
    except httpx.RequestError as e:
        error_msg = f"Request error calling {{url}}: {{str(e)}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg}})
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {{e.response.status_code}} calling {{url}}: {{e.response.text}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg}})
    except Exception as e:
        error_msg = f"Unexpected error in {tool_name}: {{str(e)}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg}})
'''

        return ServerFile(
            path=f"tools/{tool_name}.py",
            content=content,
            description=f"Implementation for {tool_name} tool",
        )

    def _generate_resource_files(
        self, resources: List[Dict[str, Any]], base_url: Optional[str]
    ) -> List[ServerFile]:
        """Generate resource implementation files."""
        if not resources:
            return [
                ServerFile(
                    path="resources/__init__.py",
                    content="# No resources generated",
                    description="Empty resources module",
                )
            ]

        files = []

        # Generate resources __init__.py
        resource_imports = []
        for resource in resources:
            resource_name = resource.get("name", "unknown_resource")
            resource_imports.append(
                f"from .{resource_name.lower().replace(' ', '_')} import {resource_name.lower().replace(' ', '_')}_handler"
            )

        init_content = f'''"""
Resource implementations for the MCP server.
"""
{chr(10).join(resource_imports)}

__all__ = [
{chr(10).join([f'    "{resource.get("name", "unknown_resource").lower().replace(" ", "_")}_handler",' for resource in resources])}
]
'''

        files.append(
            ServerFile(
                path="resources/__init__.py",
                content=init_content,
                description="Resources module initialization",
            )
        )

        # Generate individual resource files
        for resource in resources:
            resource_file = self._generate_resource_file(resource, base_url)
            files.append(resource_file)

        return files

    def _generate_resource_file(
        self, resource: Dict[str, Any], base_url: Optional[str]
    ) -> ServerFile:
        """Generate individual resource implementation."""
        resource_name = resource.get("name", "unknown_resource")
        clean_name = resource_name.lower().replace(" ", "_")
        description = resource.get("description", f"Resource: {resource_name}")

        # Extract API metadata if available
        api_metadata = resource.get("api_metadata", {})

        if api_metadata and api_metadata.get("path"):
            # Resource backed by API endpoint
            method = api_metadata.get("method", "GET").upper()
            path = api_metadata.get("path", "/")
            url = f"{base_url or 'https://api.example.com'}{path}"

            content = f'''"""
{resource_name} resource implementation.
"""
import json
from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)

async def {clean_name}_handler(uri: str) -> str:
    """
    {description}
    
    Args:
        uri: Resource URI
        
    Returns:
        Resource content as JSON string
    """
    try:
        async with httpx.AsyncClient() as client:
            # Make API request to get resource data
            url = "{url}"
            method = "{method}"
            
            logger.info(f"Fetching resource data from {{url}}")
            
            if method == "GET":
                response = await client.get(url)
            else:
                # For resources, we typically use GET
                response = await client.get(url)
            
            response.raise_for_status()
            
            # Return the resource data
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
            else:
                data = response.text
            
            result = {{
                "uri": uri,
                "content": data,
                "mime_type": "application/json",
                "metadata": {{
                    "source_url": url,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type")
                }}
            }}
            
            return json.dumps(result, indent=2)
            
    except httpx.RequestError as e:
        error_msg = f"Request error fetching resource {{uri}}: {{str(e)}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg, "uri": uri}})
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {{e.response.status_code}} fetching resource {{uri}}: {{e.response.text}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg, "uri": uri}})
    except Exception as e:
        error_msg = f"Unexpected error fetching resource {{uri}}: {{str(e)}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg, "uri": uri}})
'''
        else:
            # Schema-based resource
            schema = resource.get("resource_schema", {})
            content = f'''"""
{resource_name} resource implementation.
"""
import json
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)

async def {clean_name}_handler(uri: str) -> str:
    """
    {description}
    
    Args:
        uri: Resource URI
        
    Returns:
        Resource schema as JSON string
    """
    try:
        # Return the schema definition
        schema = {json.dumps(schema, indent=2) if schema else "{}"}
        
        result = {{
            "uri": uri,
            "content": schema,
            "mime_type": "application/json",
            "metadata": {{
                "type": "schema",
                "resource_name": "{resource_name}"
            }}
        }}
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"Error providing schema resource {{uri}}: {{str(e)}}"
        logger.error(error_msg)
        return json.dumps({{"error": error_msg, "uri": uri}})
'''

        return ServerFile(
            path=f"resources/{clean_name}.py",
            content=content,
            description=f"Implementation for {resource_name} resource",
        )

    def _generate_config_file(self, request: ServerGenerationRequest) -> ServerFile:
        """Generate configuration file."""
        content = f'''"""
Configuration for {request.server_name} MCP Server.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration."""
    
    # Server settings
    server_name: str = "{request.server_name}"
    server_description: str = "{request.server_description or f'MCP server for {request.server_name}'}"
    version: str = "{request.version}"
    
    # API settings
    base_url: Optional[str] = "{request.base_url or 'https://api.example.com'}"
    timeout: int = 30
    max_retries: int = 3
    
    # Authentication settings
    authentication: Optional[Dict[str, Any]] = {request.authentication or {}}
    
    # Logging settings
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "MCP_SERVER_"
'''

        return ServerFile(
            path="config.py", content=content, description="Server configuration"
        )

    def _generate_setup_files(
        self, request: ServerGenerationRequest
    ) -> List[ServerFile]:
        """Generate setup files for the package."""
        package_name = request.package_name or request.server_name.lower().replace(
            " ", "_"
        )

        # Generate pyproject.toml
        pyproject_content = f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "{request.version}"
description = "{request.server_description or f'MCP server for {request.server_name}'}"
authors = [
    {{name = "{request.author or 'Generated'}", email = "generated@example.com"}},
]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "mcp>=0.5.0",
    "pydantic>=2.0.0", 
    "httpx>=0.24.0",
    "structlog>=21.1.0"
]

[project.scripts]
{package_name} = "{package_name}.server:main"
"""

        # Generate README.md
        readme_content = f"""# {request.server_name} MCP Server

{request.server_description or f"MCP server for {request.server_name}"}

Generated by API-to-MCP-Generator.

## Installation

```bash
pip install -e .
```

## Usage

```bash
{package_name}
```

## Tools

This server provides {len(request.tools)} tools:

{chr(10).join([f"- **{tool.get('name', 'unknown')}**: {tool.get('description', 'No description')}" for tool in request.tools])}

## Resources

This server provides {len(request.resources)} resources:

{chr(10).join([f"- **{resource.get('name', 'unknown')}**: {resource.get('description', 'No description')}" for resource in request.resources])}
"""

        return [
            ServerFile(
                path="pyproject.toml",
                content=pyproject_content,
                description="Python package configuration",
            ),
            ServerFile(
                path="README.md",
                content=readme_content,
                description="Package documentation",
            ),
        ]


# Import here to avoid circular imports
from .template_generator import TemplateGenerator
