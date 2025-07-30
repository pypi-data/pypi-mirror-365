# Omni-FS MCP Server

Omni-FS-MCP is an MCP (Model Context Protocol) server that supports managing multiple types of file systems simultaneously, such as local FS, S3, R2, B2, WebDAV, and others, in one unified MCP server. It is built on top of OpenDAL and provides comprehensive multi-backend support.

## Features

- **Multiple Backend Support**: Manage multiple file systems simultaneously (local, S3, WebDAV, etc.)
- **Dual Transport Support**: Supports both stdio and streamable-http transports

## Installation

```bash
# Install using uv (recommended)
uv add omni-fs-mcp

# Or install using pip
pip install omni-fs-mcp
```

## Quick Start

### Single Backend Mode (Backward Compatible)

```bash
# Local filesystem
omni-fs-mcp-stdio "fs:///"

# S3
omni-fs-mcp-http "s3://bucket-name?region=us-east-1&access_key_id=xxx&secret_access_key=yyy"

# WebDAV
omni-fs-mcp-stdio "webdav://example.com/webdav?username=user&password=pass"

# Memory (for testing)
omni-fs-mcp-stdio "memory:///"
```

### Multi-Backend Mode with Configuration

Create a configuration file (`backends.json`):

```json
{
  "backends": [
    {
      "name": "local",
      "url": "fs:///",
      "description": "Local filesystem access",
      "default": true
    },
    {
      "name": "s3-prod",
      "url": "s3://my-bucket?region=us-east-1&access_key_id=AKIA...&secret_access_key=...",
      "description": "Production S3 bucket",
      "readonly": false
    },
    {
      "name": "backup",
      "url": "s3://backup-bucket?region=us-west-2&access_key_id=...",
      "description": "Backup storage (read-only)",
      "readonly": true
    }
  ]
}
```

Start the server with the configuration:

```bash
# Stdio transport
omni-fs-mcp-stdio backends.json

# Or HTTP transport
omni-fs-mcp-http --config backends.json --port 8080
```

## Available Tools

### File Operations

All file operations support an optional `backend` parameter. If not specified, the default backend is used.

1. **list_files(path="/", backend=None)** - List files and directories
2. **read_file(path, backend=None)** - Read file contents as text
3. **write_file(path, content, backend=None)** - Write content to a file
4. **copy_file(src, dst, src_backend=None, dst_backend=None)** - Copy files (supports cross-backend)
5. **rename_file(src, dst, backend=None)** - Rename or move files/directories
6. **create_dir(path, backend=None)** - Create a directory
7. **stat_file(path, backend=None)** - Get file/directory metadata

### Backend Management

8. **register_backend(name, url, ...)** - Register a new backend
9. **list_backends()** - List all registered backends
10. **set_default_backend(name)** - Set the default backend
11. **remove_backend(name, force=False)** - Remove a backend
12. **check_backend_health(backend=None)** - Check backend connectivity
13. **get_backend_stats()** - Get backend statistics

## Configuration

### JSON Configuration Properties

- **name** (required): Unique backend identifier (alphanumeric, hyphens, underscores only)
- **url** (required): Backend connection URL
- **description** (optional): Human-readable description
- **default** (optional): Set as default backend (default: false)
- **readonly** (optional): Prevent write operations (default: false)
- **timeout** (optional): Connection timeout in seconds (default: 30)
- **retry_attempts** (optional): Retry attempts for failed operations (default: 3)
- **validate_connection** (optional): Validate connection during registration (default: true)

### Supported Backends

Thanks to OpenDAL, this MCP server supports numerous storage backends:

| Backend Type | URL Scheme | Example URL |
|-------------|------------|-------------|
| Local Filesystem | `fs://` | `fs:///` |
| AWS S3 | `s3://` | `s3://bucket?region=us-east-1&access_key_id=...` |
| WebDAV | `webdav://` | `webdav://server.com/path?username=user&password=pass` |
| In-Memory | `memory://` | `memory:///` |
| FTP | `ftp://` | `ftp://server.com:21?username=user&password=pass` |
| HTTP/HTTPS | `http://`, `https://` | `https://files.example.com/api` |
| And many more | Various | See [OpenDAL documentation](https://opendal.apache.org/) |

## Usage Examples

### Cross-Backend Operations

```python
# Backup local file to S3
copy_file("/important/document.pdf", "/backups/document.pdf",
          src_backend="local", dst_backend="s3-backup")

# Sync from production to staging
copy_file("/data/config.json", "/staging/config.json",
          src_backend="s3-prod", dst_backend="s3-staging")
```

### Backend Management

```python
# Register a new backend at runtime
register_backend(
    name="temp-storage",
    url="memory:///",
    description="Temporary in-memory storage",
    set_as_default=False
)

# List all backends with their status
backends = list_backends()

# Check backend health
health = check_backend_health()  # All backends
health = check_backend_health("s3-prod")  # Specific backend
```

### Development Workflow

```python
# Work locally
write_file("/project/index.html", html_content, backend="local")

# Test and validate...

# Deploy to production
copy_file("/project/index.html", "/www/index.html",
          src_backend="local", dst_backend="webdav-server")
```

## Command Line Interface

### General Command

```bash
# Stdio transport (default)
omni-fs-mcp [--config config.json] [url] --transport stdio

# HTTP transport
omni-fs-mcp [--config config.json] [url] --transport streamable-http --port 8080
```

### Transport-Specific Commands

**For stdio transport (local connections):**
```bash
omni-fs-mcp-stdio [config.json|url]
```

**For HTTP transport (remote connections):**
```bash
omni-fs-mcp-http [--config config.json] [url] [--port 8080] [--host localhost]
```

### Transport Modes

#### Stdio Transport
- **Use case**: Local integrations, development, CLI tools
- **Advantages**: Simple setup, no network configuration
- **Communication**: Standard input/output streams

#### Streamable HTTP Transport
- **Use case**: Remote connections, web applications, cloud deployments
- **Advantages**: Network accessible, scalable, cloud-friendly
- **Communication**: HTTP with bidirectional streaming

## Advanced Features

### Read-Only Backends

Prevent accidental modifications by configuring backends as read-only:

```json
{
  "name": "backup-storage",
  "url": "s3://backup-bucket?...",
  "readonly": true
}
```

### Health Monitoring

The system provides comprehensive health monitoring:
- Connection validation during registration
- Real-time health checks via `check_backend_health()`
- Health status included in `list_backends()` output
- Automatic health updates during operations

### Error Handling

Comprehensive error handling for:
- Configuration errors (invalid names, URLs, parameters)
- Connection errors (failed backend connections)
- Operation errors (file not found, permission denied, timeouts)
- Read-only violations
- Backend not found errors

## Example Configurations

### Development Environment

```json
{
  "backends": [
    {
      "name": "local-dev",
      "url": "fs:///",
      "description": "Local development files",
      "default": true
    },
    {
      "name": "memory-temp",
      "url": "memory:///",
      "description": "Temporary storage for testing"
    }
  ]
}
```

### Production Environment

```json
{
  "backends": [
    {
      "name": "app-data",
      "url": "s3://production-app-data?region=us-east-1&access_key_id=...",
      "description": "Production application data",
      "default": true,
      "timeout": 60,
      "retry_attempts": 5
    },
    {
      "name": "user-uploads",
      "url": "s3://user-uploads-bucket?region=us-east-1&access_key_id=...",
      "description": "User uploaded files"
    },
    {
      "name": "backups",
      "url": "s3://backup-storage?region=us-west-2&access_key_id=...",
      "description": "Read-only backup storage",
      "readonly": true
    }
  ]
}
```

## Development

```bash
# Clone the repository
git clone <repository-url>
cd omni-fs-mcp

# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run the server in development
uv run omni-fs-mcp-stdio "memory:///"

# Test multi-backend setup
uv run omni-fs-mcp-stdio examples/demo_config.json
```

## Security Considerations

1. **Credential Management**: Store sensitive credentials securely, avoid hardcoding in config files
2. **Read-Only Configuration**: Use read-only backends for sensitive or archived data
3. **Network Security**: Use HTTPS/TLS for network-based backends when possible
4. **Access Control**: Implement proper IAM policies for cloud storage backends
5. **Logging**: Monitor backend access and operations for security auditing

## Troubleshooting

### Common Issues

1. **Backend Registration Fails**
   - Check URL format and credentials
   - Verify network connectivity
   - Try with `validate_connection=false` for testing

2. **Cross-Backend Copy Fails**
   - Ensure both backends are healthy
   - Check that destination backend is not read-only
   - Verify file paths exist in source backend

3. **Performance Issues**
   - Adjust timeout and retry_attempts for slow backends
   - Use health checks to identify problematic backends
   - Consider backend proximity for cross-backend operations

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Single Backend

The multi-backend server is fully backward compatible. To migrate:

1. Existing single-backend commands continue to work unchanged
2. Optionally create a configuration file for additional backends
3. Gradually adopt multi-backend features as needed

## License

This project is licensed under the MIT License.
