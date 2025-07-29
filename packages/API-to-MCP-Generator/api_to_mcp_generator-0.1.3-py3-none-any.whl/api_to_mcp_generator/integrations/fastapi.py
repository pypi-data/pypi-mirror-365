"""
FastAPI integration for api-to-mcp-generator.
"""
from fastapi import APIRouter, FastAPI, Request, HTTPException
from api_to_mcp_generator.parser import load_openapi_spec, get_api_base_url
from api_to_mcp_generator.converter import convert_to_mcp
from api_to_mcp_generator.filter import parse_filter
from typing import Optional, List

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
            spec = load_openapi_spec(
                url=current_spec_url,
                file_path=current_spec_file,
                allowed_domains=allowed_domains,
            )

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
            mcp_spec = convert_to_mcp(spec, api_base_url, auth_header, path_filter)
            return mcp_spec
        except (ConnectionError, ValueError, IOError) as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router, prefix=prefix)
