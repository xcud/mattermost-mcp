#!/usr/bin/env python3
"""
Example: Test Mattermost MCP connection
"""

import os
import sys
from pathlib import Path

# Add the project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mattermost_mcp.client import MattermostClient

def test_connection():
    """
    Test the Mattermost client connection.
    
    Requires environment variables:
    - MATTERMOST_URL: Your Mattermost server URL
    - MATTERMOST_TOKEN: Your bot token 
    - MATTERMOST_TEAM_ID: Your team ID (optional)
    """
    print("🧪 Testing Mattermost MCP Client...")
    
    # Check required environment variables
    required_vars = ['MATTERMOST_URL', 'MATTERMOST_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nSet them like this:")
        print("export MATTERMOST_URL='https://your-mattermost-server.com'")
        print("export MATTERMOST_TOKEN='your-bot-token-here'")
        print("export MATTERMOST_TEAM_ID='your-team-id-here'  # optional")
        return False
    
    # Initialize client
    try:
        client = MattermostClient()
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test connection
    print("🔗 Testing connection...")
    try:
        connected = client.test_connection()
        if connected:
            print("✅ Connection successful!")
            print(f"Server version: {client.get_server_version()}")
            
            # Test basic operations
            print("\n📝 Testing basic operations...")
            
            # List channels
            channels = client.get_channels()
            print(f"Found {len(channels)} accessible channels")
            
            # Get team members (if team ID provided)
            if os.getenv('MATTERMOST_TEAM_ID'):
                try:
                    members = client.get_team_members()
                    print(f"Found {len(members)} team members")
                except Exception as e:
                    print(f"Team members query failed: {e}")
            
            print("\n🎉 All tests passed! MCP server ready for use.")
            return True
        else:
            print("❌ Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
