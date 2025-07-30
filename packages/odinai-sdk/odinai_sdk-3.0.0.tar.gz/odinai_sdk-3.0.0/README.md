# Odin AI Python SDK

[![PyPI version](https://badge.fury.io/py/odinai-sdk.svg)](https://badge.fury.io/py/odinai-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/odinai-sdk.svg)](https://pypi.org/project/odinai-sdk/)

Official Python client library for the [Odin AI](https://getodin.ai) API.

## Installation

```bash
pip install odinai-sdk
```

## Quick Start

```python
from odin_sdk import OdinClient

# Initialize the client
client = OdinClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
    host="https://api.getodin.ai"  # optional, defaults to production
)

# Create a project
project = client.projects.create(
    name="My Project",
    description="A test project"
)

# Start a chat
chat = client.chats.create(
    project_id=project.id,
    message="Hello, Odin!"
)

print(f"Response: {chat.response}")
```

## Features

- **Clean, Resource-based API**: Intuitive interface organized by resources (projects, chats, agents, etc.)
- **Type Safety**: Full type hints for better IDE support and code completion
- **Error Handling**: Meaningful exceptions for different error conditions
- **Authentication**: Automatic API key and secret management
- **Async Support**: Coming soon!

## Documentation

For detailed documentation and examples, visit [docs.getodin.ai](https://docs.getodin.ai)

## API Resources

- **Projects**: Create and manage AI projects
- **Chats**: Have conversations with AI agents
- **Agents**: Manage and configure AI agents  
- **Knowledge Base**: Upload and manage knowledge base entries
- **Data Types**: Define custom data types
- **Roles**: Manage user roles and permissions

## Support

- GitHub Issues: [github.com/getodin/odin-sdk/issues](https://github.com/getodin/odin-sdk/issues)
- Email: [support@getodin.ai](mailto:support@getodin.ai)
- Documentation: [docs.getodin.ai](https://docs.getodin.ai)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
