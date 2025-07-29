"""
FastAPI integration for api-to-mcp-generator.
"""

from fastapi import APIRouter, FastAPI, Request, HTTPException
from pydantic import BaseModel
from api_to_mcp_generator.parser import load_openapi_spec, get_api_base_url
from api_to_mcp_generator.converter import convert_to_mcp, convert_to_mcp_enhanced
from api_to_mcp_generator.filter import parse_filter
from api_to_mcp_generator.codegen.server_generator import ServerGenerator
from api_to_mcp_generator.models.server import (
    ServerGenerationRequest,
    ServerGenerationResponse,
)
from api_to_mcp_generator.utils.logging import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)
from typing import Optional, List, Dict, Any

logger = get_logger(__name__)


def add_mcp_route(
    app: FastAPI,
    prefix: str = "/mcp",
    openapi_url: Optional[str] = None,
    openapi_file: Optional[str] = None,
    allowed_domains: Optional[List[str]] = None,
):
    """
    Adds an MCP route to a FastAPI application.
    It can be configured with a default OpenAPI spec (from a URL or a local file)
    and can be dynamically overridden by query parameters.

    :param app: The FastAPI application instance.
    :param prefix: The path prefix for the MCP endpoint.
    :param openapi_url: A default URL for the OpenAPI specification.
    :param openapi_file: A path to a default local OpenAPI specification file.
    :param allowed_domains: A list of allowed domains for the 's' parameter to prevent SSRF.
    """
    if openapi_url and openapi_file:
        raise ValueError("Provide either 'openapi_url' or 'openapi_file', not both.")

    router = APIRouter()

    @router.get("")
    async def get_mcp_spec(request: Request):
        """
        Returns the MCP specification based on query parameters.
        - s: (Optional) URL of the OpenAPI specification file. Overrides the default.
        - u: (Optional) Base URL of the target API. If not provided, it's inferred from the spec.
        - h: (Optional) Authentication header format (e.g., "Authorization:Bearer")
        - f: (Optional) Path filter expressions
        """
        spec_url_query = request.query_params.get("s")
        api_base_url_override = request.query_params.get("u")
        auth_header = request.query_params.get("h")
        filter_str = request.query_params.get("f")

        # Determine the source of the OpenAPI spec
        current_spec_url = spec_url_query or openapi_url
        current_spec_file = None if spec_url_query else openapi_file

        if not current_spec_url and not current_spec_file:
            raise HTTPException(
                status_code=400,
                detail="Missing OpenAPI spec. Provide it via the 's' query parameter or configure a default spec for the route.",
            )

        try:
            log_operation_start(
                "load_openapi_spec",
                {"url": current_spec_url, "file_path": current_spec_file},
            )
            spec = load_openapi_spec(
                url=current_spec_url,
                file_path=current_spec_file,
                allowed_domains=allowed_domains,
            )
            log_operation_success("load_openapi_spec")

            # Use the override if provided, otherwise try to infer it from the spec
            # For local files, relative server URLs cannot be resolved, so an override or absolute URL in the spec is needed.
            spec_location_for_resolution = current_spec_url if current_spec_url else ""
            api_base_url = api_base_url_override or get_api_base_url(
                spec, spec_location_for_resolution
            )

            if not api_base_url:
                raise HTTPException(
                    status_code=400,
                    detail="Missing API base URL. Could not infer from spec. Please provide it via the 'u' query parameter.",
                )

            path_filter = parse_filter(filter_str) if filter_str else None
            log_operation_start(
                "convert_to_mcp_enhanced",
                {"api_base_url": api_base_url, "auth_header": auth_header},
            )
            mcp_result = convert_to_mcp_enhanced(
                spec, api_base_url, auth_header=auth_header, path_filter=path_filter
            )
            log_operation_success("convert_to_mcp_enhanced")
            return mcp_result.server
        except (ConnectionError, ValueError, IOError) as e:
            logger.error("Error processing MCP spec request", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router, prefix=prefix)


def add_server_generation_routes(
    app: FastAPI,
    prefix: str = "/generate",
    allowed_domains: Optional[List[str]] = None,
):
    """
    Adds server generation routes to a FastAPI application.

    :param app: The FastAPI application instance.
    :param prefix: The path prefix for the generation endpoints.
    :param allowed_domains: A list of allowed domains for SSRF protection.
    """
    router = APIRouter()
    server_generator = ServerGenerator()

    class ConvertRequest(BaseModel):
        """Request for OpenAPI to MCP conversion."""

        openapi_spec_url: Optional[str] = None
        openapi_spec_file: Optional[str] = None
        server_name: Optional[str] = None
        api_base_url: Optional[str] = None
        auth_header: Optional[str] = None
        filter_expression: Optional[str] = None

    @router.post("/convert")
    async def convert_openapi_to_mcp(request: ConvertRequest):
        """
        Convert OpenAPI specification to MCP format using enhanced models.
        """
        try:
            # Load OpenAPI spec
            log_operation_start(
                "load_openapi_spec",
                {
                    "url": request.openapi_spec_url,
                    "file_path": request.openapi_spec_file,
                },
            )
            spec = load_openapi_spec(
                url=request.openapi_spec_url,
                file_path=request.openapi_spec_file,
                allowed_domains=allowed_domains,
            )
            log_operation_success("load_openapi_spec")

            # Determine base URL
            spec_location = request.openapi_spec_url if request.openapi_spec_url else ""
            api_base_url = request.api_base_url or get_api_base_url(spec, spec_location)

            if not api_base_url:
                raise HTTPException(
                    status_code=400,
                    detail="Missing API base URL. Could not infer from spec. Please provide it in api_base_url field.",
                )

            # Apply filters
            path_filter = (
                parse_filter(request.filter_expression)
                if request.filter_expression
                else None
            )

            # Convert to MCP
            log_operation_start(
                "convert_to_mcp_enhanced",
                {"api_base_url": api_base_url, "auth_header": request.auth_header},
            )
            result = convert_to_mcp_enhanced(
                spec,
                api_base_url,
                request.server_name,
                request.auth_header,
                path_filter,
            )
            log_operation_success("convert_to_mcp_enhanced")

            return result.model_dump()

        except Exception as e:
            logger.error("Error converting OpenAPI to MCP", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/server")
    async def generate_mcp_server(
        request: ServerGenerationRequest,
    ) -> ServerGenerationResponse:
        """
        Generate a complete MCP server implementation from MCP tools and resources.
        """
        try:
            log_operation_start("generate_server", {"server_name": request.server_name})
            result = server_generator.generate_server(request)
            log_operation_success("generate_server")
            return result

        except Exception as e:
            logger.error("Error generating MCP server", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

    class FullGenerationRequest(BaseModel):
        """Request for complete OpenAPI to MCP server generation."""

        openapi_spec_url: Optional[str] = None
        openapi_spec_file: Optional[str] = None
        server_name: str
        server_description: Optional[str] = None
        package_name: Optional[str] = None
        version: str = "1.0.0"
        author: Optional[str] = None
        api_base_url: Optional[str] = None
        auth_header: Optional[str] = None
        filter_expression: Optional[str] = None

    @router.post("/full")
    async def generate_full_server(
        request: FullGenerationRequest,
    ) -> ServerGenerationResponse:
        """
        Complete pipeline: OpenAPI -> MCP -> Server Generation in one step.
        """
        try:
            # Step 1: Load and convert OpenAPI spec
            log_operation_start(
                "load_openapi_spec",
                {
                    "url": request.openapi_spec_url,
                    "file_path": request.openapi_spec_file,
                },
            )
            spec = load_openapi_spec(
                url=request.openapi_spec_url,
                file_path=request.openapi_spec_file,
                allowed_domains=allowed_domains,
            )
            log_operation_success("load_openapi_spec")

            spec_location = request.openapi_spec_url if request.openapi_spec_url else ""
            api_base_url = request.api_base_url or get_api_base_url(spec, spec_location)

            if not api_base_url:
                raise HTTPException(
                    status_code=400,
                    detail="Missing API base URL. Could not infer from spec.",
                )

            path_filter = (
                parse_filter(request.filter_expression)
                if request.filter_expression
                else None
            )

            log_operation_start(
                "convert_to_mcp_enhanced",
                {"api_base_url": api_base_url, "auth_header": request.auth_header},
            )
            mcp_result = convert_to_mcp_enhanced(
                spec,
                api_base_url,
                request.server_name,
                request.auth_header,
                path_filter,
            )
            log_operation_success("convert_to_mcp_enhanced")

            # Step 2: Generate server from MCP
            server_request = ServerGenerationRequest(
                server_name=request.server_name,
                server_description=request.server_description,
                package_name=request.package_name,
                version=request.version,
                author=request.author,
                tools=[tool.model_dump() for tool in mcp_result.server.tools],
                resources=[
                    resource.model_dump() for resource in mcp_result.server.resources
                ],
                base_url=api_base_url,
                authentication=(
                    {"type": "bearer", "header": request.auth_header}
                    if request.auth_header
                    else None
                ),
            )

            log_operation_start("generate_server", {"server_name": request.server_name})
            result = server_generator.generate_server(server_request)
            log_operation_success("generate_server")

            # Add conversion metadata
            result.metadata.update(
                {
                    "conversion_warnings": mcp_result.warnings,
                    "conversion_errors": mcp_result.errors,
                    "original_api_version": mcp_result.metadata.get("api_version"),
                    "total_paths_processed": mcp_result.metadata.get("total_paths"),
                }
            )

            return result

        except Exception as e:
            logger.error("Error in full server generation pipeline", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router, prefix=prefix)
