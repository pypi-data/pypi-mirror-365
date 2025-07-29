"""
This module provides the core functionality for parsing OpenAPI specifications.
"""

import yaml
import requests
from urllib.parse import urlparse, urljoin
from typing import Optional, List
import os
from .utils.logging import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
    log_api_request,
)
import time

logger = get_logger(__name__)


def is_allowed_domain(url: str, allowed_domains: list[str]) -> bool:
    """
    Checks if the domain of the given URL is in the list of allowed domains.
    """
    if not allowed_domains:
        # If the list is empty or None, allow all domains.
        logger.debug("No domain restrictions configured, allowing all domains")
        return True

    domain = urlparse(url).netloc
    is_allowed = domain in allowed_domains
    logger.debug(
        "Domain check",
        domain=domain,
        allowed=is_allowed,
        allowed_domains=allowed_domains,
    )
    return is_allowed


def load_openapi_spec(
    url: Optional[str] = None,
    file_path: Optional[str] = None,
    allowed_domains: list[str] = None,
) -> dict:
    """
    Loads an OpenAPI specification from a URL or a local file path.
    Supports both JSON and YAML formats.
    """
    log_operation_start(
        "load_openapi_spec",
        {
            "source_type": "url" if url else "file",
            "source": url or file_path,
            "has_domain_restrictions": bool(allowed_domains),
        },
        logger,
    )

    if url:
        if not is_allowed_domain(url, allowed_domains):
            error_msg = f"URL domain '{urlparse(url).netloc}' is not an allowed domain."
            logger.error(
                "Domain validation failed",
                url=url,
                domain=urlparse(url).netloc,
                allowed_domains=allowed_domains,
            )
            raise ConnectionError(error_msg)

        try:
            start_time = time.time()
            response = requests.get(url)
            response_time = time.time() - start_time
            response.raise_for_status()

            log_api_request(
                "GET", url, response.status_code, response_time, logger=logger
            )
            spec_content = response.text
            logger.info(
                "Successfully fetched OpenAPI spec from URL",
                url=url,
                content_length=len(spec_content),
            )

        except requests.exceptions.RequestException as e:
            log_operation_error("load_openapi_spec", e, {"url": url}, logger)
            raise ConnectionError(
                f"Failed to fetch OpenAPI spec from {url}: {e}"
            ) from e
    elif file_path:
        try:
            logger.debug("Loading OpenAPI spec from file", file_path=file_path)
            with open(file_path, "r") as f:
                spec_content = f.read()
            logger.info(
                "Successfully loaded OpenAPI spec from file",
                file_path=file_path,
                content_length=len(spec_content),
            )
        except FileNotFoundError:
            error = ValueError(f"File not found at path: {file_path}")
            log_operation_error(
                "load_openapi_spec", error, {"file_path": file_path}, logger
            )
            raise error
        except Exception as e:
            error = IOError(f"Failed to read file at {file_path}: {e}")
            log_operation_error(
                "load_openapi_spec", error, {"file_path": file_path}, logger
            )
            raise error from e
    else:
        error = ValueError("Either 'url' or 'file_path' must be provided.")
        log_operation_error("load_openapi_spec", error, {}, logger)
        raise error

    try:
        # Try to parse as JSON first, then fall back to YAML
        logger.debug("Parsing OpenAPI specification content")
        try:
            spec = yaml.safe_load(spec_content)
            logger.info(
                "Successfully parsed OpenAPI spec",
                format="YAML/JSON",
                openapi_version=spec.get("openapi", spec.get("swagger", "unknown")),
                title=spec.get("info", {}).get("title", "unknown"),
            )

            log_operation_success(
                "load_openapi_spec",
                {
                    "source": url or file_path,
                    "openapi_version": spec.get("openapi", spec.get("swagger")),
                    "paths_count": len(spec.get("paths", {})),
                },
                logger,
            )

            return spec
        except ValueError:
            spec = yaml.safe_load(spec_content)
            logger.info(
                "Successfully parsed OpenAPI spec",
                format="YAML/JSON",
                openapi_version=spec.get("openapi", spec.get("swagger", "unknown")),
                title=spec.get("info", {}).get("title", "unknown"),
            )

            log_operation_success(
                "load_openapi_spec",
                {
                    "source": url or file_path,
                    "openapi_version": spec.get("openapi", spec.get("swagger")),
                    "paths_count": len(spec.get("paths", {})),
                },
                logger,
            )

            return spec
    except yaml.YAMLError as e:
        error = ValueError(f"Failed to parse OpenAPI spec: {e}")
        log_operation_error(
            "load_openapi_spec", error, {"source": url or file_path}, logger
        )
        raise error from e


def parse_openapi_spec(spec: dict) -> dict:
    """
    Parses a loaded OpenAPI specification to extract relevant information
    for MCP conversion.
    """
    logger.debug("Parsing OpenAPI spec structure")

    # For now, this is a simple pass-through.
    # In the future, this can be expanded to perform more complex parsing
    # and validation of the spec.
    if "openapi" not in spec or not spec["openapi"].startswith("3."):
        error = ValueError("Only OpenAPI 3.x specifications are supported.")
        logger.error(
            "Unsupported OpenAPI version",
            version=spec.get("openapi", spec.get("swagger", "unknown")),
        )
        raise error

    result = {
        "paths": spec.get("paths", {}),
        "servers": spec.get("servers", []),
        "components": spec.get("components", {}),
    }

    logger.info(
        "Parsed OpenAPI spec structure",
        paths_count=len(result["paths"]),
        servers_count=len(result["servers"]),
        has_components=bool(result["components"]),
    )

    return result


def get_api_base_url(spec: dict, spec_url: str) -> Optional[str]:
    """
    Extracts the base URL from the OpenAPI spec.
    If the spec provides a relative URL, it's resolved against the spec's own URL.
    """
    logger.debug("Extracting API base URL", spec_url=spec_url)

    # OpenAPI v3
    if "servers" in spec and spec["servers"]:
        server_url_str = spec["servers"][0]["url"]
        logger.debug("Found servers section", server_url=server_url_str)

        parsed_url = urlparse(server_url_str)
        # Check if the URL has a scheme and network location to determine if it's absolute.
        # This is a more compatible way than using is_absolute().
        if parsed_url.scheme and parsed_url.netloc:
            base_url = server_url_str.rstrip("/")
            logger.info("Using absolute server URL", base_url=base_url)
            return base_url
        else:
            # It's a relative path, join it with the spec's base URL
            base_url = urljoin(spec_url, server_url_str).rstrip("/")
            logger.info(
                "Resolved relative server URL",
                relative_url=server_url_str,
                base_url=base_url,
            )
            return base_url

    # OpenAPI v2 (Swagger)
    if "host" in spec:
        scheme = spec.get("schemes", ["https"])[0]
        host = spec["host"]
        base_path = spec.get("basePath", "").rstrip("/")
        base_url = f"{scheme}://{host}{base_path}"
        logger.info(
            "Using Swagger v2 host configuration",
            scheme=scheme,
            host=host,
            base_path=base_path,
            base_url=base_url,
        )
        return base_url

    logger.warning("No base URL found in OpenAPI spec")
    return None
