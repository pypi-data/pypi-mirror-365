# Changelog

All notable changes to the API-to-MCP Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-27

### Added

- **Complete MCP Server Generation**: Generate standalone, runnable MCP server packages from any OpenAPI spec
- **Resource Generation**: Transform GET endpoints and schemas into MCP resources for data access
- **Structured Logging**: Comprehensive logging with `structlog` across all modules
- **Advanced Security**: SSRF protection with domain whitelisting for remote spec loading
- **Path Filtering**: Selective endpoint exposure with configurable path filters
- **Authentication Forwarding**: Support for forwarding authentication headers to upstream APIs
- **Unicode Support**: Full support for international APIs with special characters and emojis
- **FastAPI Integration**: Drop-in FastAPI routes for dynamic OpenAPI-to-MCP conversion
- **Comprehensive Testing**: 71 tests with 100% pass rate, including E2E and security tests
- **Production Documentation**: Complete documentation suite with guides, examples, and API reference

### Changed

- **Enhanced Parameter Handling**: Improved parameter extraction and validation
- **Better Error Handling**: More descriptive error messages and warning system
- **Pydantic v2 Support**: Full compatibility with Pydantic v2 models
- **Code Quality**: Full type hints and improved code structure

### Technical Details

- **Core Functions**: `convert_spec_to_mcp()` with comprehensive options
- **Models**: Robust Pydantic models for MCP tools, resources, and server configuration
- **Security**: Built-in SSRF protection and input validation
- **Performance**: Optimized schema resolution and reference handling
- **Testing**: E2E tests, integration tests, security tests, and edge case coverage

## [0.1.0] - Initial Release

### Features

- Basic OpenAPI to MCP conversion functionality
- Simple tool generation from API endpoints
- Basic FastAPI integration
- Initial test suite

---

## Upcoming Features (Roadmap)

### v0.3.0 (Planned)

- Enhanced authentication methods (OAuth, API keys)
- Custom template support for server generation
- Plugin system for custom converters
- Performance optimizations for large APIs

### v0.4.0 (Planned)

- CLI tool for command-line usage
- Docker containerization support
- Advanced caching mechanisms
- Webhook support for dynamic API updates

### v1.0.0 (Planned)

- Stable public API
- Production deployment guides
- Enterprise features
- Long-term support commitment

---

## Migration Guide

### From v0.1.x to v0.2.0

The v0.2.0 release introduces several breaking changes:

1. **Function Signature Changes**: `convert_spec_to_mcp()` is the main conversion function
2. **Model Changes**: Resources now use structured models instead of simple dictionaries
3. **New Dependencies**: `structlog` is now required for logging functionality

**Before (v0.1.x):**

```python
from api_to_mcp_generator import convert_openapi_to_mcp
result = convert_openapi_to_mcp(spec_url)
```

**After (v0.2.0):**

```python
from api_to_mcp_generator import convert_spec_to_mcp
result = convert_spec_to_mcp(
    url=spec_url,
    api_base_url="https://api.example.com"
)
```

See the [Migration Guide](docs/guides/migration.md) for detailed upgrade instructions.
