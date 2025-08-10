"""
Tests for Mattermost MCP

Basic test suite to validate functionality
"""

import pytest
import os
from unittest.mock import Mock, patch
from mattermost_mcp import MattermostClient, MattermostAPIError


class TestMattermostClient:
    """Test the Mattermost API client"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_url = "https://test.mattermost.com"
        self.test_token = "test_token_123"
        self.test_team_id = "team_123"
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = MattermostClient(
            url=self.test_url,
            token=self.test_token,
            team_id=self.test_team_id
        )
        
        assert client.url == self.test_url + "/"
        assert client.token == self.test_token
        assert client.team_id == self.test_team_id
        assert client.api_url == f"{self.test_url}/api/v4/"
    
    def test_client_initialization_from_env(self):
        """Test client initialization from environment variables"""
        with patch.dict(os.environ, {
            'MATTERMOST_URL': self.test_url,
            'MATTERMOST_TOKEN': self.test_token,
            'MATTERMOST_TEAM_ID': self.test_team_id
        }):
            client = MattermostClient()
            assert client.url == self.test_url + "/"
            assert client.token == self.test_token
            assert client.team_id == self.test_team_id
    
    def test_missing_credentials(self):
        """Test error handling for missing credentials"""
        with pytest.raises(ValueError, match="Mattermost URL and token are required"):
            MattermostClient(url=None, token=None)
    
    @patch('requests.Session.request')
    def test_successful_api_call(self, mock_request):
        """Test successful API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'id': 'test_id', 'name': 'test'}
        mock_request.return_value = mock_response
        
        client = MattermostClient(url=self.test_url, token=self.test_token)
        result = client._get_json('test/endpoint')
        
        assert result == {'id': 'test_id', 'name': 'test'}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {'message': 'Not found'}
        mock_request.return_value = mock_response
        
        client = MattermostClient(url=self.test_url, token=self.test_token)
        
        with pytest.raises(MattermostAPIError) as exc_info:
            client._get_json('test/endpoint')
        
        assert exc_info.value.status_code == 404
        assert "Not found" in str(exc_info.value)
    
    @patch('requests.Session.request')
    def test_rate_limiting(self, mock_request):
        """Test rate limiting functionality"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client = MattermostClient(url=self.test_url, token=self.test_token)
        
        # Make multiple requests rapidly
        import time
        start_time = time.time()
        for _ in range(3):
            client._get_json('test/endpoint')
        end_time = time.time()
        
        # Should take at least some time due to rate limiting
        assert end_time - start_time >= 0.2  # 3 requests * 0.1s min interval
    
    def test_cache_functionality(self):
        """Test caching of API responses"""
        with patch.object(MattermostClient, '_get_json') as mock_get:
            mock_get.return_value = [{'id': 'team1', 'name': 'Team 1'}]
            
            client = MattermostClient(url=self.test_url, token=self.test_token)
            
            # First call should hit API
            result1 = client.get_teams()
            assert mock_get.call_count == 1
            
            # Second call should use cache
            result2 = client.get_teams()
            assert mock_get.call_count == 1  # Still only 1 call
            assert result1 == result2


class TestMattermostMCPServer:
    """Test the MCP server implementation"""
    
    def test_server_initialization(self):
        """Test MCP server initialization"""
        from mattermost_mcp.server import MattermostMCPServer
        
        server = MattermostMCPServer()
        assert server.server is not None
        assert server.client is None  # Should be lazy-loaded
    
    @pytest.mark.asyncio
    async def test_tool_listing(self):
        """Test that tools are properly listed"""
        from mattermost_mcp.server import MattermostMCPServer
        
        server = MattermostMCPServer()
        tools = await server.server.list_tools()
        
        # Check that we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'list_channels', 'create_channel', 'search_messages',
            'send_message', 'search_users', 'get_user_profile'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names


if __name__ == "__main__":
    pytest.main([__file__])
