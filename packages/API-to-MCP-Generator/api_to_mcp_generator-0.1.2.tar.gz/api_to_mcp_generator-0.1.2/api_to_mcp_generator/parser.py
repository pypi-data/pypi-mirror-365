"""
This module provides the core functionality for parsing OpenAPI specifications.
"""
import yaml
import requests
from urllib.parse import urlparse, urljoin
from typing import Optional, List

def is_allowed_domain(url: str, allowed_domains: list[str]) -> bool:
    """
    Checks if the domain of the given URL is in the list of allowed domains.
    """
    if not allowed_domains:
        # If the list is empty or None, allow all domains.
        return True
    
    domain = urlparse(url).netloc
    return domain in allowed_domains

def load_openapi_spec(url: str, allowed_domains: list[str] = None) -> dict:
    """
    Loads an OpenAPI specification from a URL with domain validation.
    Supports both JSON and YAML formats.
    """
    if not is_allowed_domain(url, allowed_domains):
        raise ConnectionError(f"URL domain '{urlparse(url).netloc}' is not an allowed domain.")

    try:
        response = requests.get(url)
        response.raise_for_status()
        # Try to parse as JSON first, then fall back to YAML
        try:
            return response.json()
        except ValueError:
            return yaml.safe_load(response.text)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch OpenAPI spec from {url}: {e}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse OpenAPI spec as YAML from {url}: {e}") from e

def parse_openapi_spec(spec: dict) -> dict:
    """
    Parses a loaded OpenAPI specification to extract relevant information
    for MCP conversion.
    """
    # For now, this is a simple pass-through.
    # In the future, this can be expanded to perform more complex parsing
    # and validation of the spec.
    if "openapi" not in spec or not spec["openapi"].startswith("3."):
        raise ValueError("Only OpenAPI 3.x specifications are supported.")

    return {
        "paths": spec.get("paths", {}),
        "servers": spec.get("servers", []),
        "components": spec.get("components", {}),
    }

def get_api_base_url(spec: dict, spec_url: str) -> Optional[str]:
    """
    Extracts the base URL from the OpenAPI spec.
    If the spec provides a relative URL, it's resolved against the spec's own URL.
    """
    # OpenAPI v3
    if "servers" in spec and spec["servers"]:
        server_url_str = spec["servers"][0]["url"]
        
        parsed_url = urlparse(server_url_str)
        # Check if the URL has a scheme and network location to determine if it's absolute.
        # This is a more compatible way than using is_absolute().
        if parsed_url.scheme and parsed_url.netloc:
            return server_url_str.rstrip("/")
        else:
            # It's a relative path, join it with the spec's base URL
            return urljoin(spec_url, server_url_str).rstrip("/")

    # OpenAPI v2 (Swagger)
    if "host" in spec:
        scheme = spec.get("schemes", ["https"])[0]
        host = spec["host"]
        base_path = spec.get("basePath", "").rstrip("/")
        return f"{scheme}://{host}{base_path}"

    return None


def _is_domain_allowed(url: str, allowed_domains: List[str]) -> bool:
    """Checks if the domain of the given URL is in the list of allowed domains."""
    if not allowed_domains:
        # If the list is empty or None, allow all domains.
        return True
    
    domain = urlparse(url).netloc
    return domain in allowed_domains
