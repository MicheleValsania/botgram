"""Instagram client module."""
import requests
from requests.exceptions import RequestException
from typing import Dict, Tuple, Optional, Any

from src.backend.instagram.session import InstagramSessionManager
from src.backend.config import InstagramConfig

class InstagramClient:
    """Instagram client for making requests to Instagram API."""

    def __init__(self, username: str):
        """Initialize Instagram client.
        
        Args:
            username: Instagram username
        
        Raises:
            ValueError: If no valid session is found
        """
        self.username = username
        self.session = InstagramSessionManager.get_session(username)
        if not self.session or not self.session.is_valid:
            raise ValueError('No valid session found')

    def _make_request(self, method: str, url: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Make a request to Instagram API.
        
        Args:
            method: HTTP method
            url: Request URL
            data: Request data
            params: Request parameters
        
        Returns:
            Tuple of response data and status code
        """
        if not self.session or not self.session.is_valid:
            return {
                'error': 'Invalid session',
                'error_code': 'INVALID_SESSION'
            }, 401

        try:
            headers = {
                'User-Agent': self.session.user_agent,
                'Cookie': f'sessionid={self.session.cookies.get("sessionid")}'
            }

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                timeout=30
            )

            if response.status_code == 429:
                return {
                    'error': 'Rate limit exceeded',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }, 429

            return response.json(), response.status_code

        except RequestException as e:
            return {
                'error': str(e),
                'error_code': 'REQUEST_FAILED'
            }, 500

    def follow_user(self, user_id: str) -> Tuple[Dict, int]:
        """Follow a user.
        
        Args:
            user_id: ID of user to follow
        
        Returns:
            Tuple of response data and status code
        """
        url = f"{InstagramConfig.BASE_URL}/web/friendships/{user_id}/follow/"
        return self._make_request('POST', url)

    def like_post(self, media_id: str) -> Tuple[Dict, int]:
        """Like a post.
        
        Args:
            media_id: ID of media to like
        
        Returns:
            Tuple of response data and status code
        """
        url = f"{InstagramConfig.BASE_URL}/web/likes/{media_id}/like/"
        return self._make_request('POST', url)

    def comment_post(self, media_id: str, comment_text: str) -> Tuple[Dict, int]:
        """Comment on a post.
        
        Args:
            media_id: ID of media to comment on
            comment_text: Comment text
        
        Returns:
            Tuple of response data and status code
        """
        url = f"{InstagramConfig.BASE_URL}/web/comments/{media_id}/add/"
        data = {'comment_text': comment_text}
        return self._make_request('POST', url, data=data)

    def logout(self) -> Tuple[Dict, int]:
        """Logout from Instagram.
        
        Returns:
            Tuple of response data and status code
        """
        response, status_code = self._make_request('POST', InstagramConfig.LOGOUT_URL)
        
        if status_code == 200:
            InstagramSessionManager.invalidate_session(self.username)
        
        return response, status_code
