# API-to-MCP Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL--2.0-yellow.svg)](https://opensource.org/licenses/MPL-2.0)
[![Tests](https://img.shields.io/badge/tests-71%20passed-brightgreen.svg)](https://github.com/itssri5/openapi-to-mcp/actions)
[![PyPI version](https://badge.fury.io/py/api-to-mcp-generator.svg)](https://badge.fury.io/py/api-to-mcp-generator)

**Transform any OpenAPI specification into a production-ready MCP (Model Context Protocol) server with zero manual coding.**

A powerful Python library that automatically converts OpenAPI v2/v3 specifications into complete, runnable MCP servers that AI agents can consume. Features FastAPI integration, SSRF protection, structured logging, and comprehensive testing.

## 🎯 What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that enables AI assistants to securely connect to data sources and tools. By converting your existing APIs to MCP format, you make them instantly available to AI agents like Claude, GPT-4, and other MCP-compatible systems.

## 🚀 Key Features

### **Universal API Support**

- **Any OpenAPI 3.x API** - GitHub, Stripe, Petstore, your custom APIs
- **Multiple Formats** - JSON and YAML specifications
- **Local & Remote** - Load specs from URLs or local files
- **Real-time Conversion** - Dynamic API-to-MCP transformation

### **Complete MCP Implementation**

- **🛠️ MCP Tools** - Convert API endpoints to callable functions
- **📦 MCP Resources** - Transform GET endpoints and schemas to readable resources  
- **🔧 Server Generation** - Generate complete, runnable MCP server packages
- **⚡ FastAPI Integration** - Drop-in integration for existing applications

### **Production Ready**

- **🔒 SSRF Protection** - Built-in security with domain whitelisting
- **📊 Structured Logging** - Comprehensive logging with `structlog`
- **🧪 Fully Tested** - 71 tests with 100% pass rate
- **🏗️ Type Safe** - Full Pydantic v2 models and type hints

### **Advanced Features**

- **Path Filtering** - Selectively expose API endpoints
- **Authentication** - Forward auth headers to upstream APIs
- **Schema Resolution** - Automatic `$ref` resolution for complex schemas
- **Unicode Support** - Handle international APIs with special characters

## 📖 Documentation

**📚 [Complete Documentation](docs/README.md)**

### Quick Links

- **[Installation Guide](docs/guides/installation.md)** - Get started in minutes
- **[Quick Start Guide](docs/guides/quickstart.md)** - 5-minute tutorial
- **[API Reference](docs/api/core-functions.md)** - Detailed API documentation  
- **[Advanced Examples](docs/examples/advanced-usage.md)** - Complex scenarios
- **[Troubleshooting](docs/guides/troubleshooting.md)** - Common issues and solutions

## 📦 Installation

```bash
pip install api-to-mcp-generator
```

Or with Poetry:

```bash
poetry add api-to-mcp-generator
```

## 🚀 Quick Start

### 1. Convert Any API to MCP (30 seconds)

```python
from api_to_mcp_generator import convert_spec_to_mcp

# Convert Petstore API to MCP format
result = convert_spec_to_mcp(
    url="https://petstore3.swagger.io/api/v3/openapi.json",
    api_base_url="https://petstore3.swagger.io/api/v3"
)

print(f"✅ Generated {len(result.server.tools)} MCP tools")
print(f"✅ Generated {len(result.server.resources)} MCP resources")

# Each API endpoint becomes an MCP tool
for tool in result.server.tools[:3]:
    print(f"🛠️  {tool.name}: {tool.description}")
```

### 2. FastAPI Gateway Example

Use our pre-built FastAPI gateway for HTTP-based conversion:

```python
# Run the included FastAPI gateway
# This provides a web service for converting OpenAPI specs
python examples/fastapi_gateway.py
```

**Test it:**

```bash
# Convert Petstore API via HTTP
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://petstore3.swagger.io/api/v3/openapi.json",
    "api_base_url": "https://petstore3.swagger.io/api/v3"
  }'

# Or test other APIs
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.github.com/openapi.json", 
    "api_base_url": "https://api.github.com"
  }'
```

### 3. Generate Complete MCP Server Package

Generate a standalone, runnable MCP server:

```python
from api_to_mcp_generator import convert_spec_to_mcp
from api_to_mcp_generator.codegen.server_generator import ServerGenerator, ServerGenerationRequest

# Step 1: Convert API
result = convert_spec_to_mcp(
    url="https://api.github.com/openapi.json",
    api_base_url="https://api.github.com"
)

# Step 2: Generate server package
request = ServerGenerationRequest(
    server_name="GitHub MCP Server",
    package_name="github_mcp_server",
    version="1.0.0",
    author="Your Name",
    tools=[tool.model_dump() for tool in result.server.tools],
    resources=[resource.model_dump() for resource in result.server.resources],
    base_url="https://api.github.com"
)

generator = ServerGenerator()
server_response = generator.generate_server(request)

# Step 3: Write to disk
import os
for file in server_response.package.files:
    os.makedirs(os.path.dirname(file.path), exist_ok=True)
    with open(file.path, 'w') as f:
        f.write(file.content)

print(f"🎉 Generated complete MCP server with {len(server_response.package.files)} files")
print("🚀 Ready to run: python server.py")
```

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Functions](#-core-functions)
- [FastAPI Integration](#-fastapi-integration)
- [Server Generation](#️-server-generation)
- [Configuration](#-configuration)
- [Security](#-security)
- [Examples](#-examples)
- [Development](#-development)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

## 🔧 Core Functions

### `convert_spec_to_mcp()`

Convert any OpenAPI spec to MCP format with tools and resources:

```python
from api_to_mcp_generator import convert_spec_to_mcp

# From URL
result = convert_spec_to_mcp(
    url="https://api.example.com/openapi.json",
    api_base_url="https://api.example.com/v1"
)

# From local file  
result = convert_spec_to_mcp(
    file_path="./specs/my-api.json",
    api_base_url="https://localhost:3000"
)
```

**Returns:** `MCPConversionResult` with:

- `server: MCPServer` - Complete MCP server definition
- `metadata: dict` - API metadata (title, version, etc.)

### Generated MCP Tools

Every HTTP operation becomes an MCP tool:

```python
# GET /pets → 
{
    "name": "listPets",
    "description": "List all pets", 
    "inputSchema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "How many items to return"}
        }
    }
}

# POST /pets →
{
    "name": "createPet", 
    "description": "Create a new pet",
    "inputSchema": {
        "type": "object", 
        "properties": {
            "name": {"type": "string"},
            "tag": {"type": "string"}
        },
        "required": ["name"]
    }
}
```

### Generated MCP Resources

GET endpoints and schemas become MCP resources:

```python
# GET /pets/status → 
{
    "name": "listPets",
    "description": "List all pets",
    "uri": "api://pets", 
    "mimeType": "application/json"
}

# Schema: Pet →
{
    "name": "PetSchema",
    "description": "Schema definition for Pet", 
    "uri": "schema://pet",
    "mimeType": "application/json"
}
```

## ⚡ FastAPI Integration

The library includes a pre-built FastAPI gateway for web-based conversion:

### Using the Built-in Gateway

```python
# Start the gateway server
python examples/fastapi_gateway.py
```

This provides a complete web service with:

- **HTTP endpoint** for converting OpenAPI specs
- **Built-in validation** and error handling
- **CORS support** for web applications
- **Interactive documentation** at `/docs`

### Gateway API Reference

**Endpoint:** `POST /convert`

**Request Body:**

```json
{
  "url": "https://api.example.com/openapi.json",
  "api_base_url": "https://api.example.com",
  "filter_tags": ["users", "products"],  // Optional
  "include_deprecated": false            // Optional
}
```

**Response:**

```json
{
  "tools": [...],     // Array of MCP tools
  "resources": [...], // Array of MCP resources
  "metadata": {...}   // API metadata
}
```

### Configuration Options

The FastAPI gateway supports these configuration options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `HOST` | `str` | `"0.0.0.0"` | Server host address |
| `PORT` | `int` | `8000` | Server port |
| `LOG_LEVEL` | `str` | `"info"` | Logging level |

Set via environment variables:

```bash
export HOST=localhost
export PORT=3000
export LOG_LEVEL=debug
python examples/fastapi_gateway.py
```

## 🏗️ Server Generation

Generate complete, runnable MCP server packages:

### Basic Server Generation

```python
from api_to_mcp_generator.codegen.server_generator import ServerGenerator, ServerGenerationRequest

# First, convert your API
result = convert_spec_to_mcp(
    url="https://api.example.com/openapi.json", 
    api_base_url="https://api.example.com"
)

# Generate server package
request = ServerGenerationRequest(
    server_name="Example API MCP Server",
    package_name="example_mcp",
    version="1.0.0",
    author="Your Name",
    tools=[tool.model_dump() for tool in result.server.tools],
    resources=[resource.model_dump() for resource in result.server.resources],
    base_url="https://api.example.com"
)

generator = ServerGenerator()
package = generator.generate_server(request)

print(f"Generated {len(package.package.files)} files")
# Files include: server.py, tools/*.py, resources/*.py, requirements.txt
```

### Server Generation Options

The `ServerGenerationRequest` supports these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `server_name` | `str` | Yes | Human-readable server name |
| `package_name` | `str` | Yes | Python package name |
| `version` | `str` | Yes | Package version |
| `author` | `str` | Yes | Package author |
| `tools` | `List[dict]` | Yes | MCP tools to include |
| `resources` | `List[dict]` | Yes | MCP resources to include |
| `base_url` | `str` | Yes | API base URL |
| `description` | `str` | No | Package description |
| `license` | `str` | No | Package license |

### Generated Package Structure

```
example_mcp/
├── server.py           # Main MCP server
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── README.md          # Usage instructions
├── tools/
│   ├── __init__.py
│   ├── list_users.py  # Individual tool implementations
│   └── create_user.py
├── resources/
│   ├── __init__.py
│   └── users.py       # Resource implementations
└── pyproject.toml     # Package metadata
```

## ⚙️ Configuration

### Environment Variables

Configure the library behavior with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_TO_MCP_LOG_LEVEL` | `"INFO"` | Logging level |
| `API_TO_MCP_LOG_FORMAT` | `"json"` | Log format (json/text) |
| `API_TO_MCP_TIMEOUT` | `30` | HTTP request timeout |
| `API_TO_MCP_MAX_RETRIES` | `3` | Max retry attempts |

```python
import os
os.environ['API_TO_MCP_LOG_LEVEL'] = 'DEBUG'
os.environ['API_TO_MCP_TIMEOUT'] = '60'

from api_to_mcp_generator import convert_spec_to_mcp
```

### Advanced Configuration

```python
from api_to_mcp_generator.utils.logging import setup_logging

# Custom logging setup
setup_logging(
    json_logs=True,
    log_level="debug"
)

# Convert with custom settings
result = convert_spec_to_mcp(
    url="https://api.example.com/openapi.json",
    api_base_url="https://api.example.com",
    # Custom timeout and retries handled automatically
)
```

## 🔒 Security

### SSRF Protection

The library includes built-in Server-Side Request Forgery (SSRF) protection:

- **Domain validation** - Only allowed domains can be accessed
- **Protocol restrictions** - Only HTTP/HTTPS protocols allowed
- **IP address filtering** - Private IP ranges blocked
- **URL validation** - Malformed URLs rejected

### Security Best Practices

```python
# ✅ GOOD: Use specific allowed domains
allowed_domains = ["api.trusted-partner.com", "docs.vendor.io"]

# ❌ AVOID: Using wildcard or overly broad domains
# This is handled automatically by the library's SSRF protection
```

### Authentication Handling

The library preserves authentication headers from OpenAPI specs:

```python
# API keys and bearer tokens are automatically detected
# and included in the generated MCP tools

result = convert_spec_to_mcp(
    url="https://api.example.com/openapi.json",
    api_base_url="https://api.example.com"
)

# Generated tools will include proper authentication
# based on the OpenAPI security schemes
```

## 📚 Examples

### Basic Usage

```python
from api_to_mcp_generator import convert_spec_to_mcp

# Convert GitHub API
result = convert_spec_to_mcp(
    url="https://api.github.com/openapi.json",
    api_base_url="https://api.github.com"
)

# Access generated tools and resources
print(f"Generated {len(result.server.tools)} tools")
print(f"Generated {len(result.server.resources)} resources")

# Inspect first tool
tool = result.server.tools[0]
print(f"Tool: {tool.name} - {tool.description}")
```

### FastAPI Gateway

Use the included FastAPI gateway for web-based conversion:

```bash
# Start the gateway server
python examples/fastapi_gateway.py

# Convert APIs via HTTP POST
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://petstore3.swagger.io/api/v3/openapi.json", "api_base_url": "https://petstore3.swagger.io/api/v3"}'
```

### Complete Demo

Run the comprehensive demo:

```bash
python examples/complete_demo.py
```

This demo shows:

- Before/after comparison with manual approaches
- Live API conversion with the Petstore API
- Server generation capabilities
- Complete feature overview

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -e .

# Run all tests
pytest

# Run with coverage
pytest --cov=api_to_mcp_generator

# Run release validation
python validate_release.py
```

### Code Formatting

```bash
# Format code
black .

# Check formatting
black --check .
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs
make html
```

## 📚 API Reference

### Core Functions

#### `convert_spec_to_mcp(url=None, file_path=None, api_base_url=None)`

Convert OpenAPI specification to MCP format.

**Parameters:**

- `url` (str, optional): URL to OpenAPI specification
- `file_path` (str, optional): Path to local OpenAPI file  
- `api_base_url` (str, required): Base URL for API calls

**Returns:** `MCPConversionResult`

**Example:**

```python
result = convert_spec_to_mcp(
    url="https://api.example.com/openapi.json",
    api_base_url="https://api.example.com"
)
```

### Model Classes

#### `MCPConversionResult`

Result of OpenAPI to MCP conversion.

**Attributes:**

- `server: MCPServer` - Complete MCP server definition
- `metadata: dict` - API metadata (title, version, description)

#### `MCPServer`

MCP server definition containing tools and resources.

**Attributes:**

- `tools: List[MCPTool]` - List of MCP tools
- `resources: List[MCPResource]` - List of MCP resources

#### `MCPTool`

Individual MCP tool definition.

**Attributes:**

- `name: str` - Tool name
- `description: str` - Tool description
- `parameters: dict` - JSON schema for parameters

#### `MCPResource`

Individual MCP resource definition.

**Attributes:**

- `name: str` - Resource name
- `description: str` - Resource description
- `uri: str` - Resource URI
- `mime_type: str` - MIME type

## 🏆 Why Choose API-to-MCP Generator?

### **Production Ready**

- **71 tests with 100% pass rate** - Thoroughly tested and validated
- **Type-safe** - Full Pydantic v2 models and type hints
- **SSRF Protection** - Built-in security features
- **Comprehensive logging** - Track every conversion step

### **Developer Friendly**

- **Zero manual coding** - Automatic tool and resource generation
- **Multiple output formats** - FastAPI integration, standalone servers
- **Rich documentation** - Complete guides and examples
- **Active development** - Regular updates and improvements

### **Universal Compatibility**

- **Any OpenAPI API** - Works with GitHub, Stripe, Petstore, your custom APIs
- **Multiple formats** - JSON, YAML, local files, remote URLs
- **Framework agnostic** - Use standalone or integrate with FastAPI

## 📄 License

This project is licensed under the MPL-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -e .[dev]`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

## 📞 Support

- **Documentation**: [Complete docs](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/itssri5/openapi-to-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/itssri5/openapi-to-mcp/discussions)

---

Made with ❤️ for the MCP community
