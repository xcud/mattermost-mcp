"""
Mattermost MCP - Model Context Protocol server for Mattermost integration

This package provides comprehensive Mattermost API access for AI agents and automation systems.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .client import MattermostClient
from .server import MattermostMCPServer

__all__ = ["MattermostClient", "MattermostMCPServer"]
