# Mattermost MCP Development

## Setup for Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mattermost-mcp.git
cd mattermost-mcp
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
export MATTERMOST_URL="https://your-mattermost.example.com"
export MATTERMOST_TOKEN="your-bot-token"
export MATTERMOST_TEAM_ID="your-team-id"  # optional
```

## Getting a Bot Token

1. Go to your Mattermost server
2. Navigate to Main Menu → Integrations → Bot Accounts
3. Create a new bot account
4. Copy the access token
5. Grant the bot appropriate permissions for channels you want to access

## Running Tests

```bash
pytest tests/
```

## Code Formatting

```bash
black mattermost_mcp/
isort mattermost_mcp/
```

## Type Checking

```bash
mypy mattermost_mcp/
```

## Running the Demo

```bash
python examples/demo.py
```

## Project Structure

```
mattermost-mcp/
├── mattermost_mcp/          # Main package
│   ├── __init__.py          # Package exports
│   ├── client.py            # Mattermost API client
│   ├── server.py            # MCP server implementation
│   └── tools/               # Tool implementations
├── examples/                # Usage examples
│   ├── demo.py             # Comprehensive demo
│   └── claude_config.json  # Claude Desktop config
├── tests/                   # Test suite
├── README.md               # Project documentation
├── pyproject.toml          # Modern Python packaging
└── LICENSE                 # MIT license
```

## Adding New Tools

1. Add tool definition to `server.py` in the `list_tools()` function
2. Add tool handler in `_handle_tool_call()` method
3. If needed, add new API methods to `client.py`
4. Add tests in `tests/`
5. Update documentation

## API Coverage

Current implementation covers:
- ✅ Channel management (list, create, update, members)
- ✅ Message operations (search, send, pin)
- ✅ User operations (search, profiles, presence)
- ✅ File operations (upload, download, metadata)
- ✅ Team operations (members, stats)
- ✅ Connection testing and health checks

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Format code: `black .` and `isort .`
7. Type check: `mypy mattermost_mcp/`
8. Commit changes: `git commit -am 'Add feature'`
9. Push to branch: `git push origin feature-name`
10. Create Pull Request

## Release Process

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. Build and publish: `python -m build && twine upload dist/*`
