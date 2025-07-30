# Paramus World Client

A Python client library for interacting with the Paramus World semantic knowledge graph system.

## Features

- **JSON-RPC API Client**: Easy-to-use client for Paramus World API
- **SPARQL Support**: Execute SPARQL queries and updates against the knowledge graph
- **Chat Interface**: Submit messages to the AI assistant
- **Health Monitoring**: Check system status and statistics
- **Authentication**: JWT token-based authentication

## Installation

```bash
pip install paramus-world
```

## Quick Start

```python
from paramus.world.client import ParamusWorldClient

# Initialize the client
client = ParamusWorldClient(token="your-jwt-token")

# Check system health
health = client.check_system_health()
print(health)

# Submit a chat message
response = client.submit_chat("Hello, World!")
print(response)

# Execute a SPARQL query
query = """
PREFIX world: <https://paramus.ai/world/>
SELECT ?subject ?predicate ?object
WHERE { ?subject ?predicate ?object }
LIMIT 10
"""
result = client.sparql_query(query)
print(result)
```

## API Methods

### Authentication
- `authenticate(username, password)` - Authenticate and get a token

### Chat Interface  
- `submit_chat(message, context=None)` - Submit a message to the AI assistant

### SPARQL Operations
- `sparql_query(query, format="json")` - Execute SPARQL queries
- `sparql_update(update)` - Execute SPARQL updates

### System Monitoring
- `check_system_health()` - Get system health and statistics

## Configuration

The client connects to `http://127.0.0.1:8051` by default. You can configure this:

```python
client = ParamusWorldClient(
    base_url="https://your-server.com",
    token="your-jwt-token"
)
```

## Examples

See the [examples](https://github.com/gressling/paramus-world-client/tree/main/examples) directory for comprehensive usage examples.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Repository**: https://github.com/gressling/paramus-world-client
- **Documentation**: https://paramus-world-client.readthedocs.io/
- **Issues**: https://github.com/gressling/paramus-world-client/issues
