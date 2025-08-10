#!/usr/bin/env python3
"""
Mattermost MCP Usage Example

This example demonstrates how to use the Mattermost MCP server
with various operations for autonomous AI agents.
"""

import asyncio
import json
import os
from mattermost_mcp import MattermostClient


async def demo_mattermost_operations():
    """Demonstrate various Mattermost operations"""
    
    # Initialize client
    print("🔗 Connecting to Mattermost...")
    client = MattermostClient()
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to Mattermost")
        return
    
    print(f"✅ Connected to Mattermost {client.get_server_version()}")
    
    # Get teams and channels
    print("\n📋 Getting team information...")
    teams = client.get_teams()
    print(f"Teams: {[team['display_name'] for team in teams]}")
    
    channels = client.get_channels()
    print(f"Channels: {[ch['display_name'] for ch in channels[:5]]}...")  # First 5
    
    # Search for users
    print("\n👥 Searching for users...")
    users = client.search_users("ben", limit=3)
    for user in users:
        print(f"- {user['username']} ({user.get('first_name', '')} {user.get('last_name', '')})")
    
    # Search messages
    print("\n🔍 Searching recent messages...")
    try:
        search_results = client.search_posts("project", per_page=3)
        if search_results.get('posts'):
            print(f"Found {len(search_results['posts'])} messages containing 'project'")
            for post_id, post in list(search_results['posts'].items())[:2]:
                print(f"- {post['message'][:100]}...")
        else:
            print("No messages found")
    except Exception as e:
        print(f"Search failed: {e}")
    
    # Get channel statistics
    if channels:
        print(f"\n📊 Getting statistics for channel: {channels[0]['display_name']}")
        try:
            stats = client.get_channel_stats(channels[0]['id'])
            print(f"Members: {stats.get('member_count', 'unknown')}")
            print(f"Posts: {stats.get('pinnedpost_count', 'unknown')} pinned")
        except Exception as e:
            print(f"Stats failed: {e}")
    
    # Demonstrate file operations (if you have a test file)
    test_file = "/tmp/mattermost_test.txt"
    if os.path.exists(test_file) and channels:
        print(f"\n📎 Uploading test file...")
        try:
            with open(test_file, 'w') as f:
                f.write("This is a test file from Mattermost MCP")
            
            upload_result = client.upload_file(channels[0]['id'], test_file)
            print(f"✅ File uploaded: {upload_result.get('file_infos', [{}])[0].get('name', 'unknown')}")
            
            # Clean up
            os.remove(test_file)
        except Exception as e:
            print(f"File upload failed: {e}")


def demo_channel_management():
    """Demonstrate channel management operations"""
    print("\n🏗️ Channel Management Demo")
    
    client = MattermostClient()
    
    # Create a test channel
    channel_name = f"test-mcp-{int(asyncio.get_event_loop().time())}"
    print(f"Creating channel: {channel_name}")
    
    try:
        new_channel = client.create_channel(
            name=channel_name,
            display_name="MCP Test Channel",
            purpose="Testing Mattermost MCP functionality",
            header="🤖 AI Agent Testing Zone"
        )
        print(f"✅ Created channel: {new_channel['display_name']}")
        
        # Update channel header
        client.update_channel_header(
            new_channel['id'], 
            "🤖 AI Agent Testing Zone - Updated via MCP"
        )
        print("✅ Updated channel header")
        
        # Get channel info
        channel_info = client.get_channel_info(new_channel['id'])
        print(f"Channel purpose: {channel_info.get('purpose', 'none')}")
        
    except Exception as e:
        print(f"❌ Channel operations failed: {e}")


def demo_autonomous_agent_workflow():
    """Demonstrate a typical autonomous AI agent workflow"""
    print("\n🤖 Autonomous Agent Workflow Demo")
    
    client = MattermostClient()
    
    # 1. Survey the team landscape
    print("1. 🔍 Surveying team landscape...")
    teams = client.get_teams()
    channels = client.get_channels()
    members = client.get_team_members()
    
    print(f"   Found {len(teams)} teams, {len(channels)} channels, {len(members)} members")
    
    # 2. Identify active channels
    print("2. 📊 Analyzing channel activity...")
    active_channels = []
    for channel in channels[:3]:  # Check first 3 channels
        try:
            stats = client.get_channel_stats(channel['id'])
            if stats.get('member_count', 0) > 1:
                active_channels.append({
                    'name': channel['display_name'],
                    'id': channel['id'],
                    'members': stats.get('member_count', 0)
                })
        except:
            pass
    
    print(f"   Active channels: {[ch['name'] for ch in active_channels]}")
    
    # 3. Search for recent project discussions
    print("3. 🔍 Searching for project discussions...")
    try:
        project_posts = client.search_posts("project OR milestone OR deadline", per_page=5)
        if project_posts.get('posts'):
            print(f"   Found {len(project_posts['posts'])} relevant discussions")
        else:
            print("   No project discussions found")
    except Exception as e:
        print(f"   Search failed: {e}")
    
    # 4. Check team member availability
    print("4. 👥 Checking team availability...")
    if members:
        try:
            user_ids = [member['user_id'] for member in members[:5]]
            statuses = client.get_users_status(user_ids)
            online_count = sum(1 for status in statuses if status.get('status') == 'online')
            print(f"   {online_count}/{len(statuses)} team members currently online")
        except Exception as e:
            print(f"   Status check failed: {e}")
    
    print("\n🎯 Agent workflow complete - ready for autonomous operation!")


if __name__ == "__main__":
    print("🚀 Mattermost MCP Demo")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('MATTERMOST_URL') or not os.getenv('MATTERMOST_TOKEN'):
        print("❌ Please set MATTERMOST_URL and MATTERMOST_TOKEN environment variables")
        exit(1)
    
    # Run demos
    asyncio.run(demo_mattermost_operations())
    demo_channel_management()  
    demo_autonomous_agent_workflow()
    
    print("\n✅ Demo complete!")
