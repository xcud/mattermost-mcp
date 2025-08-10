# Mattermost MCP

A Model Context Protocol (MCP) server for comprehensive Mattermost integration. This tool provides AI agents and automation systems with full access to Mattermost's capabilities beyond basic messaging.

## Features

### Core Capabilities
- **Message Management**: Search, retrieve, and analyze message history
- **Channel Operations**: Create, manage, and monitor channels
- **User & Team Management**: Access user profiles, team structures, and presence
- **File Operations**: Upload, download, and manage file attachments
- **Advanced Search**: Find conversations, users, and content across your workspace

### Designed For
- **Autonomous AI agents** requiring Mattermost context and control
- **Automation developers** building Mattermost integrations  
- **Teams** creating custom workflow tools
- **Research applications** analyzing communication patterns

## Quick Start

### Installation

```bash
pip install mattermost-mcp
```

### Configuration

Create a configuration file or set environment variables:

```bash
export MATTERMOST_URL="https://your-mattermost.example.com"
export MATTERMOST_TOKEN="your-bot-token"
export MATTERMOST_TEAM_ID="your-team-id"  # optional
```

### Usage with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "mattermost": {
      "command": "python",
      "args": ["-m", "mattermost_mcp"],
      "env": {
        "MATTERMOST_URL": "https://your-mattermost.example.com",
        "MATTERMOST_TOKEN": "your-bot-token"
      }
    }
  }
}
```

## Available Tools

### Channel Management
- `list_channels` - Get all accessible channels
- `create_channel` - Create new channels
- `get_channel_info` - Get detailed channel information
- `add_user_to_channel` - Manage channel membership
- `set_channel_header` - Update channel descriptions

### Message Operations  
- `search_messages` - Search message history with filters
- `get_channel_messages` - Retrieve recent messages from channels
- `send_message` - Send messages to channels
- `update_message` - Edit existing messages
- `pin_message` - Pin important messages

### User & Team Operations
- `list_team_members` - Get team member directory
- `get_user_profile` - Access detailed user information
- `get_user_presence` - Check online/offline status
- `list_teams` - Get team structure information

### File Management
- `upload_file` - Upload files to channels
- `download_file` - Download shared files
- `list_files` - Get file listings for channels
- `get_file_info` - Access file metadata

### Advanced Features
- `get_analytics` - Channel and user activity analytics
- `search_users` - Find users by name, email, or criteria
- `get_channel_stats` - Message counts, activity metrics

## API Reference

[Detailed API documentation coming soon]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [Claude-Mattermost Bridge](https://github.com/yourusername/claude-mattermost-bridge) - Real-time message relay between Claude and Mattermost
- [Mattermost API Documentation](https://api.mattermost.com/)

## Support

- GitHub Issues for bug reports and feature requests
- Mattermost API documentation for API reference
- MCP specification for protocol details
