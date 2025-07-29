"""
This module handles the conversion of a parsed OpenAPI specification into an
MCP-compliant format.
"""

from typing import Callable, Optional, Dict, Any, List
from .resolver import resolve_ref
from .models.mcp import (
    MCPTool,
    MCPResource,
    MCPServer,
    MCPConversionResult,
    MCPApiMetadata,
    MCPServerInfo,
    MCPParameter,
    MCPParameterType,
)
from .resource_generator import ResourceGenerator
from .utils.logging import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)

logger = get_logger(__name__)


def _resolve_schema(spec: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively resolves $ref pointers in a schema object.
    """
    if "$ref" in schema:
        return resolve_ref(spec, schema["$ref"])

    resolved_schema = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            resolved_schema[key] = _resolve_schema(spec, value)
        elif isinstance(value, list):
            resolved_schema[key] = [
                _resolve_schema(spec, item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            resolved_schema[key] = value

    return resolved_schema


def convert_to_mcp(spec: Dict[str, Any], api_base_url: str) -> Dict[str, Any]:
    """
    Convert a parsed OpenAPI specification to MCP format.
    Returns a dictionary for backward compatibility with legacy tests.

    Args:
        spec: The parsed OpenAPI specification
        api_base_url: Base URL for the API

    Returns:
        Dict[str, Any]: Dictionary with "tools" key containing converted tools in legacy format
    """
    log_operation_start(
        "convert_to_mcp",
        {"api_base_url": api_base_url, "paths_count": len(spec.get("paths", {}))},
        logger,
    )

    try:
        tools = []
        info = spec.get("info", {})
        title = info.get("title", "OpenAPI Server")

        # Convert each path to MCP tools
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    tool_name = operation.get(
                        "operationId",
                        f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
                    )

                    # Convert to MCPParameter objects using our helper function
                    parameters = _convert_openapi_parameters_to_mcp(spec, operation)

                    # Create API metadata
                    api_metadata = MCPApiMetadata(
                        method=method.upper(),
                        path=path,
                        title=operation.get("summary", f"{method.upper()} {path}"),
                        version=spec.get("info", {}).get("version", "1.0.0"),
                        description=operation.get("description", ""),
                    )

                    tool = MCPTool(
                        name=tool_name,
                        description=operation.get(
                            "summary", f"{method.upper()} {path}"
                        ),
                        parameters=parameters,
                        api_metadata=api_metadata,
                    )

                    # Convert to legacy format expected by tests
                    legacy_tool = {
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    param.name: {
                                        "type": param.type.value,
                                        "description": param.description or "",
                                    }
                                    for param in parameters
                                },
                                "required": [
                                    param.name for param in parameters if param.required
                                ],
                            },
                        }
                    }
                    tools.append(legacy_tool)

        result = {"tools": tools}

        log_operation_success(
            "convert_to_mcp",
            {"tools_generated": len(tools), "server_name": title},
            logger,
        )

        return result

    except Exception as e:
        log_operation_error("convert_to_mcp", e, logger=logger)
        raise


def convert_to_mcp_enhanced(
    parsed_spec: dict,
    api_base_url: str,
    server_name: Optional[str] = None,
    auth_header: Optional[str] = None,
    path_filter: Optional[Callable[[str, str], bool]] = None,
) -> MCPConversionResult:
    """
    Enhanced conversion to MCP format using structured models with resources.
    """
    log_operation_start(
        "convert_to_mcp_enhanced",
        {
            "api_base_url": api_base_url,
            "server_name": server_name,
            "has_auth": bool(auth_header),
            "has_filter": bool(path_filter),
            "paths_count": len(parsed_spec.get("paths", {})),
        },
        logger,
    )

    try:
        tools = []
        resources = []
        warnings = []
        errors = []

        # Get server info
        info = parsed_spec.get("info", {})
        server_name_final = server_name or info.get("title", "Generated MCP Server")

        # Generate tools from API paths
        for path, path_item in parsed_spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                ]:
                    continue

                # Apply path filter if provided
                if path_filter and not path_filter(path, method):
                    continue

                try:
                    tool_name = (
                        operation.get("operationId")
                        or f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"
                    )

                    # Convert to MCPParameter objects using our helper function
                    parameters = _convert_openapi_parameters_to_mcp(
                        parsed_spec, operation
                    )

                    # Create API metadata
                    api_metadata = MCPApiMetadata(
                        method=method.upper(),
                        path=path,
                        title=operation.get("summary", f"{method.upper()} {path}"),
                        version=parsed_spec.get("info", {}).get("version", "1.0.0"),
                        description=operation.get("description", ""),
                    )

                    tool = MCPTool(
                        name=tool_name,
                        description=operation.get(
                            "summary", f"{method.upper()} {path}"
                        ),
                        parameters=parameters,
                        api_metadata=api_metadata,
                    )
                    tools.append(tool)

                except Exception as e:
                    warnings.append(
                        f"Failed to process {method.upper()} {path}: {str(e)}"
                    )

        # Generate resources using ResourceGenerator
        try:
            resource_generator = ResourceGenerator()
            resources = resource_generator.generate_resources_from_operations(
                parsed_spec, api_base_url, path_filter
            )
        except Exception as e:
            warnings.append(f"Failed to generate resources: {str(e)}")

        # Create server
        server_info = MCPServerInfo(
            name=server_name_final,
            version="1.0.0",
            base_url=api_base_url,
        )

        server = MCPServer(
            name=server_name_final,
            version="1.0.0",
            tools=tools,
            resources=resources,
            info=server_info,
        )

        result = MCPConversionResult(
            server=server,
            warnings=warnings,
            errors=errors,
            metadata={
                "converted_tools": len(tools),
                "converted_resources": len(resources),
                "api_version": parsed_spec.get("info", {}).get("version", "1.0.0"),
                "server_name": server_name_final,
            },
        )

        log_operation_success(
            "convert_to_mcp_enhanced",
            {
                "server_name": server_name_final,
                "tools_generated": len(tools),
                "resources_generated": len(resources),
                "warnings_count": len(warnings),
                "errors_count": len(errors),
            },
            logger,
        )

        return result

    except Exception as e:
        log_operation_error("convert_to_mcp_enhanced", e, logger=logger)
        raise


def convert_openapi_to_mcp(
    parsed_spec: dict,
    api_base_url: str,
    server_name: Optional[str] = None,
    auth_header: Optional[str] = None,
    path_filter: Optional[Callable[[str, str], bool]] = None,
) -> MCPConversionResult:
    """
    Legacy function name for backward compatibility.
    This function simply calls convert_to_mcp_enhanced with the same parameters.
    """
    return convert_to_mcp_enhanced(
        parsed_spec=parsed_spec,
        api_base_url=api_base_url,
        server_name=server_name,
        auth_header=auth_header,
        path_filter=path_filter,
    )


def convert_spec_to_mcp(
    api_base_url: str,
    url: Optional[str] = None,
    file_path: Optional[str] = None,
    server_name: Optional[str] = None,
    path_filter: Optional[List[str]] = None,
    auth_header: Optional[str] = None,
) -> MCPConversionResult:
    """
    Convenience function that loads an OpenAPI spec and converts it to MCP format.

    This function provides the API interface shown in documentation and examples,
    where users can pass URL or file_path directly without manually loading the spec.

    Args:
        api_base_url: Base URL for the API
        url: URL to fetch the OpenAPI specification from
        file_path: Path to a local OpenAPI specification file
        server_name: Display name for the generated MCP server
        path_filter: List of path prefixes to include (e.g., ["/users", "/products"])
        auth_header: Name of authentication header to forward

    Returns:
        MCPConversionResult with server, tools, resources, and any warnings/errors

    Example:
        >>> result = convert_spec_to_mcp(
        ...     api_base_url="https://petstore3.swagger.io/api/v3",
        ...     url="https://petstore3.swagger.io/api/v3/openapi.json"
        ... )
    """
    from .parser import load_openapi_spec
    from .filter import parse_filter

    log_operation_start(
        "convert_spec_to_mcp",
        {
            "has_url": bool(url),
            "has_file": bool(file_path),
            "api_base_url": api_base_url,
            "server_name": server_name,
            "has_filter": bool(path_filter),
            "has_auth": bool(auth_header),
        },
        logger,
    )

    try:
        # Load the OpenAPI spec
        if url:
            parsed_spec = load_openapi_spec(url=url)
        elif file_path:
            parsed_spec = load_openapi_spec(file_path=file_path)
        else:
            raise ValueError("Either 'url' or 'file_path' must be provided")

        # Convert path filter list to filter function if provided
        filter_func = None
        if path_filter:
            filter_func = parse_filter(include_paths=path_filter)

        # Call the core conversion function
        result = convert_to_mcp_enhanced(
            parsed_spec=parsed_spec,
            api_base_url=api_base_url,
            server_name=server_name,
            auth_header=auth_header,
            path_filter=filter_func,
        )

        log_operation_success(
            "convert_spec_to_mcp",
            {
                "tools_generated": len(result.server.tools),
                "resources_generated": len(result.server.resources),
            },
            logger,
        )

        return result

    except Exception as e:
        log_operation_error("convert_spec_to_mcp", e, logger=logger)
        raise


def _convert_openapi_type_to_mcp_type(openapi_type: str) -> MCPParameterType:
    """Convert OpenAPI parameter type to MCP parameter type."""
    type_mapping = {
        "string": MCPParameterType.STRING,
        "number": MCPParameterType.NUMBER,
        "integer": MCPParameterType.INTEGER,
        "boolean": MCPParameterType.BOOLEAN,
        "object": MCPParameterType.OBJECT,
        "array": MCPParameterType.ARRAY,
    }
    return type_mapping.get(openapi_type, MCPParameterType.STRING)


def _convert_openapi_parameters_to_mcp(
    spec: Dict[str, Any], operation: Dict[str, Any]
) -> List[MCPParameter]:
    """Convert OpenAPI operation parameters to MCP parameters."""
    parameters = []

    # Add path parameters
    for param in operation.get("parameters", []):
        if param.get("in") == "path":
            param_schema = param.get("schema", {"type": "string"})
            parameters.append(
                MCPParameter(
                    name=param["name"],
                    type=_convert_openapi_type_to_mcp_type(
                        param_schema.get("type", "string")
                    ),
                    description=param.get("description", ""),
                    required=param.get("required", True),
                    default=param_schema.get("default"),
                    enum=param_schema.get("enum"),
                )
            )

    # Add query parameters
    for param in operation.get("parameters", []):
        if param.get("in") == "query":
            param_schema = param.get("schema", {"type": "string"})
            parameters.append(
                MCPParameter(
                    name=param["name"],
                    type=_convert_openapi_type_to_mcp_type(
                        param_schema.get("type", "string")
                    ),
                    description=param.get("description", ""),
                    required=param.get("required", False),
                    default=param_schema.get("default"),
                    enum=param_schema.get("enum"),
                )
            )

    # Add request body parameters (from JSON schema)
    if "requestBody" in operation:
        request_body = operation["requestBody"]
        content = request_body.get("content", {})
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            resolved_schema = _resolve_schema(spec, schema)
            if resolved_schema.get("type") == "object":
                for prop_name, prop_schema in resolved_schema.get(
                    "properties", {}
                ).items():
                    parameters.append(
                        MCPParameter(
                            name=prop_name,
                            type=_convert_openapi_type_to_mcp_type(
                                prop_schema.get("type", "string")
                            ),
                            description=prop_schema.get("description", ""),
                            required=prop_name in resolved_schema.get("required", []),
                            default=prop_schema.get("default"),
                            enum=prop_schema.get("enum"),
                        )
                    )

    return parameters
