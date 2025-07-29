"""
Resource generation service for creating MCP resources from OpenAPI specifications.
"""

from typing import Dict, List, Optional, Any, Tuple, Callable
from .models.mcp import MCPResource, MCPApiMetadata
from .utils.logging import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)

logger = get_logger(__name__)


class ResourceGenerator:
    """Generates MCP resources from OpenAPI specifications."""

    def __init__(self):
        logger.debug("Initializing ResourceGenerator")
        self.resource_patterns = {
            "collection": ["list", "all", "find", "search", "get"],
            "item": ["get", "retrieve", "find"],
            "status": ["status", "health", "info"],
            "inventory": ["inventory", "stock", "count"],
        }
        logger.debug(
            "Resource patterns configured", patterns=list(self.resource_patterns.keys())
        )

    def generate_resources_from_operations(
        self,
        parsed_spec: Dict[str, Any],
        api_base_url: str,
        path_filter: Optional[Callable[[str, str], bool]] = None,
    ) -> List[MCPResource]:
        """
        Generate MCP resources from GET operations that can serve as data sources.

        Args:
            parsed_spec: Parsed OpenAPI specification
            api_base_url: Base URL for the API
            path_filter: Optional filter function to exclude certain paths

        Returns:
            List of MCPResource objects
        """
        log_operation_start(
            "generate_resources_from_operations",
            {
                "api_base_url": api_base_url,
                "paths_count": len(parsed_spec.get("paths", {})),
            },
            logger,
        )

        resources = []
        processed_operations = 0
        skipped_operations = 0

        # Process paths to find GET operations that can be resources
        for path, path_item in parsed_spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() != "get":
                    continue

                # Apply path filter if provided
                if path_filter and not path_filter(path, method):
                    continue

                logger.debug(
                    "Evaluating GET operation for resource",
                    path=path,
                    operation_id=operation.get("operationId"),
                )

                # Skip operations with required path parameters (they're more like tools)
                if self._has_required_path_params(operation):
                    skipped_operations += 1
                    logger.debug(
                        "Skipping operation with required path params", path=path
                    )
                    continue

                # Create resource from GET operation
                resource = self._create_resource_from_operation(
                    path, operation, api_base_url
                )
                if resource:
                    resources.append(resource)
                    processed_operations += 1
                    logger.debug(
                        "Created resource", resource_name=resource.name, path=path
                    )
                else:
                    skipped_operations += 1
                    logger.debug("Failed to create resource", path=path)

        logger.info(
            "Processed GET operations",
            total_operations=processed_operations + skipped_operations,
            processed=processed_operations,
            skipped=skipped_operations,
        )

        # Generate resources from schemas/components if available
        if "components" in parsed_spec and "schemas" in parsed_spec["components"]:
            logger.debug(
                "Processing schema components for resources",
                schemas_count=len(parsed_spec["components"]["schemas"]),
            )
            schema_resources = self._create_resources_from_schemas(
                parsed_spec["components"]["schemas"], api_base_url
            )
            resources.extend(schema_resources)
            logger.info("Added schema-based resources", count=len(schema_resources))

        log_operation_success(
            "generate_resources_from_operations",
            {
                "generated_resources_count": len(resources),
                "operation_resources": processed_operations,
                "schema_resources": (
                    len(schema_resources) if "schema_resources" in locals() else 0
                ),
            },
            logger,
        )

        return resources

    def _has_required_path_params(self, operation: Dict[str, Any]) -> bool:
        """Check if operation has required path parameters."""
        parameters = operation.get("parameters", [])
        for param in parameters:
            if param.get("in") == "path" and param.get("required", False):
                return True
        return False

    def _create_resource_from_operation(
        self, path: str, operation: Dict[str, Any], api_base_url: str
    ) -> Optional[MCPResource]:
        """Create a resource from a GET operation."""

        # Generate resource name
        operation_id = operation.get("operationId")
        if operation_id:
            resource_name = operation_id
        else:
            resource_name = (
                f"get_{path.replace('/', '_').replace('{', '').replace('}', '')}"
            )

        # Generate URI
        uri = f"api://{path.lstrip('/')}"

        # Create API metadata
        api_metadata = MCPApiMetadata(
            method="GET", path=path, base_url=api_base_url, operation_id=operation_id
        )

        # Extract response schema if available
        response_schema = None
        responses = operation.get("responses", {})
        if "200" in responses:
            response_200 = responses["200"]
            content = response_200.get("content", {})
            if "application/json" in content:
                response_schema = content["application/json"].get("schema", {})

        resource = MCPResource(
            name=resource_name,
            description=operation.get(
                "summary", operation.get("description", f"Resource for {path}")
            ),
            uri=uri,
            mime_type="application/json",
            resource_schema=response_schema,
            api_metadata=api_metadata,
            uri_template=path,
        )

        logger.debug(
            "Resource created from operation",
            {
                "resource_name": resource_name,
                "path": path,
                "operation_id": operation_id,
            },
        )

        return resource

    def _create_resources_from_schemas(
        self, schemas: Dict[str, Any], api_base_url: str
    ) -> List[MCPResource]:
        """Create resources from OpenAPI schema components."""
        resources = []

        for schema_name, schema_def in schemas.items():
            # Skip if not an object schema
            if schema_def.get("type") != "object":
                continue

            uri = f"schema://{schema_name.lower()}"

            resource = MCPResource(
                name=f"{schema_name}Schema",
                description=schema_def.get(
                    "description", f"Schema definition for {schema_name}"
                ),
                uri=uri,
                mime_type="application/json",
                resource_schema=schema_def,
                uri_template=f"/schemas/{schema_name.lower()}",
            )

            resources.append(resource)
            logger.debug(
                "Resource created from schema", {"schema_name": schema_name, "uri": uri}
            )

        return resources

    def categorize_resources(
        self, resources: List[MCPResource]
    ) -> Dict[str, List[MCPResource]]:
        """Categorize resources by type for better organization."""
        categories = {
            "data_endpoints": [],  # GET endpoints that return data
            "schemas": [],  # Schema definitions
            "collections": [],  # List/collection endpoints
            "search": [],  # Search/filter endpoints
        }

        for resource in resources:
            if resource.uri.startswith("schema://"):
                categories["schemas"].append(resource)
            elif resource.api_metadata and "search" in resource.name.lower():
                categories["search"].append(resource)
            elif resource.api_metadata and resource.api_metadata.path.count("/") <= 2:
                categories["collections"].append(resource)
            else:
                categories["data_endpoints"].append(resource)

        logger.info(
            "Resources categorized",
            {
                "total_resources": len(resources),
                "categories": {k: len(v) for k, v in categories.items()},
            },
        )

        return categories
