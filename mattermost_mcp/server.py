"""
Mattermost MCP Server - Model Context Protocol server implementation
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ServerCapabilities,
    ToolsCapability,
)

from .client import MattermostClient, MattermostAPIError


class MattermostMCPServer:
    """MCP Server for Mattermost operations"""
    
    def __init__(self):
        self.server = Server("mattermost-mcp")
        self.client: Optional[MattermostClient] = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP request handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Mattermost tools"""
            return [
                # Channel Management
                Tool(
                    name="list_channels",
                    description="Get all accessible channels in a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {
                                "type": "string",
                                "description": "Team ID (optional, uses default if not provided)"
                            }
                        }
                    }
                ),
                Tool(
                    name="create_channel",
                    description="Create a new channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Channel URL name (lowercase, no spaces)"},
                            "display_name": {"type": "string", "description": "Channel display name"},
                            "purpose": {"type": "string", "description": "Channel purpose/description"},
                            "header": {"type": "string", "description": "Channel header text"},
                            "channel_type": {"type": "string", "enum": ["O", "P"], "default": "O", "description": "O for open, P for private"},
                            "team_id": {"type": "string", "description": "Team ID (optional)"}
                        },
                        "required": ["name", "display_name"]
                    }
                ),
                Tool(
                    name="get_channel_info",
                    description="Get detailed information about a channel",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"}
                        },
                        "required": ["channel_id"]
                    }
                ),
                Tool(
                    name="add_user_to_channel",
                    description="Add a user to a channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"},
                            "user_id": {"type": "string", "description": "User ID to add"}
                        },
                        "required": ["channel_id", "user_id"]
                    }
                ),
                
                # Message Operations
                Tool(
                    name="search_messages",
                    description="Search for messages across channels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "team_id": {"type": "string", "description": "Team ID (optional)"},
                            "is_or_search": {"type": "boolean", "default": False, "description": "True for OR search, False for AND"},
                            "page": {"type": "integer", "default": 0, "description": "Page number"},
                            "per_page": {"type": "integer", "default": 20, "description": "Results per page"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_channel_messages",
                    description="Get recent messages from a channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"},
                            "limit": {"type": "integer", "default": 20, "description": "Number of messages to retrieve"},
                            "since_hours": {"type": "integer", "description": "Only messages from last N hours"}
                        },
                        "required": ["channel_id"]
                    }
                ),
                Tool(
                    name="send_message",
                    description="Send a message to a channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"},
                            "message": {"type": "string", "description": "Message text"},
                            "reply_to": {"type": "string", "description": "Post ID to reply to (optional)"}
                        },
                        "required": ["channel_id", "message"]
                    }
                ),
                Tool(
                    name="pin_message",
                    description="Pin a message to the channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "post_id": {"type": "string", "description": "Post ID to pin"}
                        },
                        "required": ["post_id"]
                    }
                ),
                
                # User Operations
                Tool(
                    name="search_users",
                    description="Search for users in the team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search term (username, name, email)"},
                            "team_id": {"type": "string", "description": "Team ID (optional)"},
                            "limit": {"type": "integer", "default": 20, "description": "Maximum results"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_user_profile",
                    description="Get detailed user profile information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID"}
                        },
                        "required": ["user_id"]
                    }
                ),
                Tool(
                    name="get_team_members",
                    description="Get all members of a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "string", "description": "Team ID (optional)"}
                        }
                    }
                ),
                Tool(
                    name="get_user_presence",
                    description="Get user online/offline status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID"}
                        },
                        "required": ["user_id"]
                    }
                ),
                
                # File Operations
                Tool(
                    name="upload_file",
                    description="Upload a file to a channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"},
                            "file_path": {"type": "string", "description": "Local file path"},
                            "filename": {"type": "string", "description": "Custom filename (optional)"}
                        },
                        "required": ["channel_id", "file_path"]
                    }
                ),
                Tool(
                    name="download_file",
                    description="Download a file from Mattermost",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "File ID"},
                            "save_path": {"type": "string", "description": "Local save path"}
                        },
                        "required": ["file_id", "save_path"]
                    }
                ),
                Tool(
                    name="get_file_info",
                    description="Get file metadata and information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "File ID"}
                        },
                        "required": ["file_id"]
                    }
                ),
                
                # Administrative/Analytics
                Tool(
                    name="get_channel_stats",
                    description="Get channel statistics and activity metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {"type": "string", "description": "Channel ID"}
                        },
                        "required": ["channel_id"]
                    }
                ),
                Tool(
                    name="test_connection",
                    description="Test Mattermost connection and authentication",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            if not self.client:
                self.client = MattermostClient()
            
            try:
                result = await self._handle_tool_call(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except MattermostAPIError as e:
                error_msg = f"Mattermost API Error: {e}"
                if e.status_code:
                    error_msg += f" (Status: {e.status_code})"
                return [TextContent(type="text", text=error_msg)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Route tool calls to appropriate handlers"""
        
        # Channel Management
        if name == "list_channels":
            return self.client.get_channels(arguments.get("team_id"))
        
        elif name == "create_channel":
            return self.client.create_channel(
                name=arguments["name"],
                display_name=arguments["display_name"],
                purpose=arguments.get("purpose", ""),
                header=arguments.get("header", ""),
                channel_type=arguments.get("channel_type", "O"),
                team_id=arguments.get("team_id")
            )
        
        elif name == "get_channel_info":
            return self.client.get_channel_info(arguments["channel_id"])
        
        elif name == "add_user_to_channel":
            return self.client.add_user_to_channel(
                arguments["channel_id"], 
                arguments["user_id"]
            )
        
        # Message Operations
        elif name == "search_messages":
            return self.client.search_posts(
                query=arguments["query"],
                team_id=arguments.get("team_id"),
                is_or_search=arguments.get("is_or_search", False),
                page=arguments.get("page", 0),
                per_page=arguments.get("per_page", 20)
            )
        
        elif name == "get_channel_messages":
            # Handle since_hours parameter
            since = None
            if "since_hours" in arguments:
                from datetime import datetime, timedelta
                since_time = datetime.now() - timedelta(hours=arguments["since_hours"])
                since = int(since_time.timestamp() * 1000)
            
            return self.client.get_posts(
                channel_id=arguments["channel_id"],
                per_page=arguments.get("limit", 20),
                since=since
            )
        
        elif name == "send_message":
            return self.client.send_message(
                channel_id=arguments["channel_id"],
                message=arguments["message"],
                root_id=arguments.get("reply_to")
            )
        
        elif name == "pin_message":
            return self.client.pin_message(arguments["post_id"])
        
        # User Operations
        elif name == "search_users":
            return self.client.search_users(
                query=arguments["query"],
                team_id=arguments.get("team_id"),
                limit=arguments.get("limit", 20)
            )
        
        elif name == "get_user_profile":
            return self.client.get_user_profile(arguments["user_id"])
        
        elif name == "get_team_members":
            return self.client.get_team_members(arguments.get("team_id"))
        
        elif name == "get_user_presence":
            return self.client.get_user_status(arguments["user_id"])
        
        # File Operations
        elif name == "upload_file":
            return self.client.upload_file(
                channel_id=arguments["channel_id"],
                file_path=arguments["file_path"],
                filename=arguments.get("filename")
            )
        
        elif name == "download_file":
            success = self.client.download_file(
                file_id=arguments["file_id"],
                save_path=arguments["save_path"]
            )
            return {"success": success, "saved_to": arguments["save_path"]}
        
        elif name == "get_file_info":
            return self.client.get_file_info(arguments["file_id"])
        
        # Administrative
        elif name == "get_channel_stats":
            return self.client.get_channel_stats(arguments["channel_id"])
        
        elif name == "test_connection":
            success = self.client.test_connection()
            version = self.client.get_server_version() if success else "unknown"
            return {
                "connected": success,
                "server_version": version,
                "api_url": self.client.api_url if success else None
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server"""
    server_instance = MattermostMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mattermost-mcp",
                server_version="0.1.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability()
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
