"""
Mattermost API Client - Core API wrapper for Mattermost operations
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MattermostAPIError(Exception):
    """Custom exception for Mattermost API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class MattermostClient:
    """
    Comprehensive Mattermost API client with rate limiting and error handling
    """
    
    def __init__(self, 
                 url: Optional[str] = None,
                 token: Optional[str] = None,
                 team_id: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Initialize Mattermost client
        
        Args:
            url: Mattermost server URL (or from MATTERMOST_URL env var)
            token: Bot token (or from MATTERMOST_TOKEN env var)  
            team_id: Team ID (or from MATTERMOST_TEAM_ID env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.url = url or os.getenv('MATTERMOST_URL')
        self.token = token or os.getenv('MATTERMOST_TOKEN')
        self.team_id = team_id or os.getenv('MATTERMOST_TEAM_ID')
        
        if not self.url or not self.token:
            raise ValueError("Mattermost URL and token are required")
        
        # Ensure URL ends with /
        if not self.url.endswith('/'):
            self.url += '/'
            
        self.api_url = urljoin(self.url, 'api/v4/')
        self.timeout = timeout
        
        # Set up session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],  # Updated from method_whitelist
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mattermost-MCP/0.1.0'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max
        
        # Cache for commonly accessed data
        self._user_cache = {}
        self._channel_cache = {}
        self._team_cache = {}
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with rate limiting and error handling
        """
        # Rate limiting
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = urljoin(self.api_url, endpoint)
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            self.last_request_time = time.time()
            
            if not response.ok:
                error_data = None
                try:
                    error_data = response.json()
                except:
                    pass
                
                message = f"API request failed: {response.status_code}"
                if error_data and 'message' in error_data:
                    message += f" - {error_data['message']}"
                
                raise MattermostAPIError(message, response.status_code, error_data)
            
            return response
            
        except requests.RequestException as e:
            raise MattermostAPIError(f"Request failed: {str(e)}")
    
    def _get_json(self, endpoint: str, **kwargs) -> Dict:
        """GET request returning JSON data"""
        response = self._make_request('GET', endpoint, **kwargs)
        return response.json()
    
    def _post_json(self, endpoint: str, data: Dict, **kwargs) -> Dict:
        """POST request with JSON data"""
        response = self._make_request('POST', endpoint, json=data, **kwargs)
        return response.json()
    
    def _put_json(self, endpoint: str, data: Dict, **kwargs) -> Dict:
        """PUT request with JSON data"""
        response = self._make_request('PUT', endpoint, json=data, **kwargs)
        return response.json()
    
    def _delete(self, endpoint: str, **kwargs) -> bool:
        """DELETE request"""
        response = self._make_request('DELETE', endpoint, **kwargs)
        return response.ok
    
    # ====================
    # TEAM OPERATIONS
    # ====================
    
    def get_teams(self) -> List[Dict]:
        """Get all teams the user belongs to"""
        if 'all_teams' not in self._team_cache:
            teams = self._get_json('users/me/teams')
            self._team_cache['all_teams'] = teams
        return self._team_cache['all_teams']
    
    def get_team_members(self, team_id: Optional[str] = None) -> List[Dict]:
        """Get members of a team"""
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID required")
        return self._get_json(f'teams/{team_id}/members')
    
    def get_team_stats(self, team_id: Optional[str] = None) -> Dict:
        """Get team statistics"""
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID required")
        return self._get_json(f'teams/{team_id}/stats')
    
    # ====================
    # CHANNEL OPERATIONS  
    # ====================
    
    def get_channels(self, team_id: Optional[str] = None) -> List[Dict]:
        """Get channels for a team"""
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID required")
            
        cache_key = f'channels_{team_id}'
        if cache_key not in self._channel_cache:
            channels = self._get_json(f'users/me/teams/{team_id}/channels')
            self._channel_cache[cache_key] = channels
        return self._channel_cache[cache_key]
    
    def get_channel_info(self, channel_id: str) -> Dict:
        """Get detailed channel information"""
        if channel_id not in self._channel_cache:
            channel = self._get_json(f'channels/{channel_id}')
            self._channel_cache[channel_id] = channel
        return self._channel_cache[channel_id]
    
    def create_channel(self, name: str, display_name: str, 
                      purpose: str = "", header: str = "",
                      channel_type: str = "O", team_id: Optional[str] = None) -> Dict:
        """
        Create a new channel
        
        Args:
            name: Channel URL name (lowercase, no spaces)
            display_name: Channel display name
            purpose: Channel purpose/description
            header: Channel header text
            channel_type: 'O' for open, 'P' for private
            team_id: Team ID (uses default if not provided)
        """
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID required")
            
        data = {
            'team_id': team_id,
            'name': name,
            'display_name': display_name,
            'purpose': purpose,
            'header': header,
            'type': channel_type
        }
        
        channel = self._post_json('channels', data)
        # Clear cache
        cache_key = f'channels_{team_id}'
        if cache_key in self._channel_cache:
            del self._channel_cache[cache_key]
        return channel
    
    def add_user_to_channel(self, channel_id: str, user_id: str) -> Dict:
        """Add a user to a channel"""
        data = {'user_id': user_id}
        return self._post_json(f'channels/{channel_id}/members', data)
    
    def remove_user_from_channel(self, channel_id: str, user_id: str) -> bool:
        """Remove a user from a channel"""
        return self._delete(f'channels/{channel_id}/members/{user_id}')
    
    def update_channel_header(self, channel_id: str, header: str) -> Dict:
        """Update channel header"""
        data = {'channel_id': channel_id, 'header': header}
        return self._put_json(f'channels/{channel_id}/patch', data)
    
    def update_channel_purpose(self, channel_id: str, purpose: str) -> Dict:
        """Update channel purpose"""
        data = {'channel_id': channel_id, 'purpose': purpose}
        return self._put_json(f'channels/{channel_id}/patch', data)
    
    def get_channel_members(self, channel_id: str) -> List[Dict]:
        """Get members of a channel"""
        return self._get_json(f'channels/{channel_id}/members')
    
    def get_channel_stats(self, channel_id: str) -> Dict:
        """Get channel statistics"""
        return self._get_json(f'channels/{channel_id}/stats')
    
    # ====================
    # MESSAGE OPERATIONS
    # ====================
    
    def get_posts(self, channel_id: str, page: int = 0, per_page: int = 60,
                  since: Optional[int] = None, before: Optional[str] = None,
                  after: Optional[str] = None) -> Dict:
        """
        Get posts from a channel
        
        Args:
            channel_id: Channel ID
            page: Page number for pagination
            per_page: Posts per page (max 200)
            since: Only posts modified since timestamp (ms)
            before: Only posts before this post ID
            after: Only posts after this post ID
        """
        params = {'page': page, 'per_page': min(per_page, 200)}
        if since:
            params['since'] = since
        if before:
            params['before'] = before
        if after:
            params['after'] = after
            
        return self._get_json(f'channels/{channel_id}/posts', params=params)
    
    def search_posts(self, query: str, team_id: Optional[str] = None,
                    is_or_search: bool = False, time_zone_offset: int = 0,
                    include_deleted_channels: bool = False,
                    page: int = 0, per_page: int = 20) -> Dict:
        """
        Search for posts across channels
        
        Args:
            query: Search query string
            team_id: Team to search in (uses default if not provided)
            is_or_search: True for OR search, False for AND search
            time_zone_offset: Timezone offset in seconds
            include_deleted_channels: Include results from deleted channels
            page: Page number
            per_page: Results per page
        """
        team_id = team_id or self.team_id
        if not team_id:
            raise ValueError("Team ID required")
            
        data = {
            'terms': query,
            'is_or_search': is_or_search,
            'time_zone_offset': time_zone_offset,
            'include_deleted_channels': include_deleted_channels,
            'page': page,
            'per_page': per_page
        }
        
        return self._post_json(f'teams/{team_id}/posts/search', data)
    
    def send_message(self, channel_id: str, message: str, 
                    root_id: Optional[str] = None, file_ids: Optional[List[str]] = None) -> Dict:
        """Send a message to a channel"""
        data = {
            'channel_id': channel_id,
            'message': message
        }
        if root_id:
            data['root_id'] = root_id
        if file_ids:
            data['file_ids'] = file_ids
            
        return self._post_json('posts', data)
    
    def update_message(self, post_id: str, message: str) -> Dict:
        """Update an existing message"""
        data = {'id': post_id, 'message': message}
        return self._put_json(f'posts/{post_id}', data)
    
    def delete_message(self, post_id: str) -> bool:
        """Delete a message"""
        return self._delete(f'posts/{post_id}')
    
    def pin_message(self, post_id: str) -> Dict:
        """Pin a message to the channel"""
        return self._post_json(f'posts/{post_id}/pin', {})
    
    def unpin_message(self, post_id: str) -> Dict:
        """Unpin a message from the channel"""
        return self._post_json(f'posts/{post_id}/unpin', {})
    
    # ====================
    # USER OPERATIONS
    # ====================
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile information"""
        if user_id not in self._user_cache:
            user = self._get_json(f'users/{user_id}')
            self._user_cache[user_id] = user
        return self._user_cache[user_id]
    
    def get_users_by_ids(self, user_ids: List[str]) -> List[Dict]:
        """Get multiple user profiles by IDs"""
        # Check cache first
        cached_users = []
        missing_ids = []
        
        for user_id in user_ids:
            if user_id in self._user_cache:
                cached_users.append(self._user_cache[user_id])
            else:
                missing_ids.append(user_id)
        
        # Fetch missing users
        if missing_ids:
            data = missing_ids
            fetched_users = self._post_json('users/ids', data)
            
            # Update cache
            for user in fetched_users:
                self._user_cache[user['id']] = user
            
            cached_users.extend(fetched_users)
        
        return cached_users
    
    def search_users(self, query: str, team_id: Optional[str] = None,
                    in_channel_id: Optional[str] = None, 
                    not_in_channel_id: Optional[str] = None,
                    limit: int = 50) -> List[Dict]:
        """
        Search for users
        
        Args:
            query: Search term (username, first name, last name, nickname, email)
            team_id: Team to search in
            in_channel_id: Only users in this channel
            not_in_channel_id: Only users NOT in this channel
            limit: Maximum results
        """
        data = {
            'term': query,
            'limit': limit
        }
        
        if team_id:
            data['team_id'] = team_id
        if in_channel_id:
            data['in_channel_id'] = in_channel_id
        if not_in_channel_id:
            data['not_in_channel_id'] = not_in_channel_id
            
        return self._post_json('users/search', data)
    
    def get_user_status(self, user_id: str) -> Dict:
        """Get user presence/status"""
        return self._get_json(f'users/{user_id}/status')
    
    def get_users_status(self, user_ids: List[str]) -> List[Dict]:
        """Get status for multiple users"""
        return self._post_json('users/status/ids', user_ids)
    
    # ====================
    # FILE OPERATIONS
    # ====================
    
    def upload_file(self, channel_id: str, file_path: str, 
                   filename: Optional[str] = None) -> Dict:
        """Upload a file to a channel"""
        if filename is None:
            filename = os.path.basename(file_path)
            
        with open(file_path, 'rb') as f:
            files = {
                'files': (filename, f, 'application/octet-stream')
            }
            data = {'channel_id': channel_id}
            
            # Don't use session for file uploads (different content type)
            response = requests.post(
                urljoin(self.api_url, 'files'),
                headers={'Authorization': f'Bearer {self.token}'},
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if not response.ok:
                raise MattermostAPIError(f"File upload failed: {response.status_code}")
            
            return response.json()
    
    def get_file_info(self, file_id: str) -> Dict:
        """Get file metadata"""
        return self._get_json(f'files/{file_id}/info')
    
    def download_file(self, file_id: str, save_path: str) -> bool:
        """Download a file"""
        response = self._make_request('GET', f'files/{file_id}')
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    
    def get_file_link(self, file_id: str) -> str:
        """Get public link for a file"""
        response = self._get_json(f'files/{file_id}/link')
        return response.get('link', '')
    
    # ====================
    # UTILITY METHODS
    # ====================
    
    def get_server_version(self) -> str:
        """Get Mattermost server version"""
        config = self._get_json('config/client?format=old')
        return config.get('Version', 'unknown')
    
    def test_connection(self) -> bool:
        """Test if connection and authentication work"""
        try:
            self._get_json('users/me')
            return True
        except MattermostAPIError:
            return False
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._user_cache.clear()
        self._channel_cache.clear()
        self._team_cache.clear()
