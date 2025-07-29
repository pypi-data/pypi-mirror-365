"""
FastAPI integration for openapi-to-mcp.
"""
from fastapi import APIRouter, FastAPI, Request, HTTPException
from openapi_to_mcp.parser import load_openapi_spec, get_api_base_url
from openapi_to_mcp.converter import convert_to_mcp
from openapi_to_mcp.filter import parse_filter
from typing import Optional, List

def add_mcp_route(
    app: FastAPI, 
    prefix: str = "/mcp", 
    allowed_domains: Optional[List[str]] = None
):
    """
    Adds an MCP route to a FastAPI application.
    It reads configuration from query parameters: s, u, h, f.

    :param app: The FastAPI application instance.
    :param prefix: The path prefix for the MCP endpoint.
    :param allowed_domains: A list of allowed domains for the 's' parameter to prevent SSRF.
    """
    router = APIRouter()

    @router.get("")
    async def get_mcp_spec(request: Request):
        """
        Returns the MCP specification based on query parameters.
        - s: URL of the OpenAPI specification file
        - u: (Optional) Base URL of the target API. If not provided, it's inferred from the spec.
        - h: Authentication header format (e.g., "Authorization:Bearer")
        - f: Path filter expressions
        """
        spec_url = request.query_params.get("s")
        api_base_url_override = request.query_params.get("u")
        auth_header = request.query_params.get("h")
        filter_str = request.query_params.get("f")

        if not spec_url:
            raise HTTPException(status_code=400, detail="Missing OpenAPI spec URL. Provide it via the 's' query parameter.")

        try:
            spec = load_openapi_spec(spec_url, allowed_domains=allowed_domains)
            
            # Use the override if provided, otherwise try to infer it from the spec
            api_base_url = api_base_url_override or get_api_base_url(spec, spec_url)

            if not api_base_url:
                raise HTTPException(status_code=400, detail="Missing API base URL. Could not infer from spec. Please provide it via the 'u' query parameter.")

            path_filter = parse_filter(filter_str) if filter_str else None
            mcp_spec = convert_to_mcp(spec, api_base_url, auth_header, path_filter)
            return mcp_spec
        except (ConnectionError, ValueError) as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router, prefix=prefix)
