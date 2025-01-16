"""
Instagram client module for making API requests with proper rate limiting and session management.
"""
import logging
import json
import time
from typing import Optional, Dict, Any, Tuple
import requests
from requests.exceptions import RequestException

from .session import InstagramSessionManager, InstagramSession
from ..config import InstagramConfig
from ..middleware.response import APIResponse

logger = logging.getLogger(__name__)

class InstagramClient:
    """Client for making Instagram API requests with proper session and rate limiting."""
    
    def __init__(self, username: str, session: Optional[InstagramSession] = None):
        self.username = username
        self.session = session or InstagramSessionManager.get_session(username)
        if not self.session:
            raise ValueError(f"No valid session found for user: {username}")
            
        self.http_session = requests.Session()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Sets up the HTTP session with proper headers and cookies."""
        self.http_session.cookies.update(self.session.cookies)
        self.http_session.headers.update({
            'User-Agent': self.session.user_agent,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-IG-App-ID': '936619743392459',
            'X-Instagram-AJAX': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def _make_request(self, method: str, url: str, 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Makes a request to Instagram with proper error handling and rate limiting."""
        try:
            if not self.session.is_valid:
                return APIResponse.error(
                    "Invalid session", 
                    error_code="INVALID_SESSION",
                    status_code=401
                )
                
            response = self.http_session.request(
                method=method,
                url=url,
                data=data,
                params=params,
                timeout=30
            )
            
            # Update session state
            self.session.update_last_action()
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning(f"Rate limit exceeded for user: {self.username}")
                return APIResponse.error(
                    "Rate limit exceeded", 
                    error_code="RATE_LIMIT_EXCEEDED",
                    status_code=429
                )
            
            # Handle other error responses
            if response.status_code >= 400:
                error_msg = f"Instagram API error: {response.status_code}"
                logger.error(f"{error_msg} - {response.text}")
                return APIResponse.error(
                    error_msg,
                    error_code="INSTAGRAM_API_ERROR",
                    status_code=response.status_code
                )
            
            return APIResponse.success(response.json())
            
        except RequestException as e:
            logger.error(f"Request failed for user {self.username}: {str(e)}")
            return APIResponse.error(
                f"Request failed: {str(e)}",
                error_code="REQUEST_FAILED",
                status_code=500
            )
    
    def follow_user(self, user_id: str) -> Tuple[Dict, int]:
        """Follows a user on Instagram."""
        if not self.session.can_perform_action('follow'):
            return APIResponse.error(
                "Daily follow limit reached",
                error_code="FOLLOW_LIMIT_REACHED",
                status_code=429
            )
        
        url = f"{InstagramConfig.BASE_URL}/web/friendships/{user_id}/follow/"
        response, status_code = self._make_request('POST', url)
        
        if status_code == 200:
            self.session.record_action('follow')
            
        return response, status_code
    
    def like_post(self, media_id: str) -> Tuple[Dict, int]:
        """Likes a post on Instagram."""
        if not self.session.can_perform_action('like'):
            return APIResponse.error(
                "Daily like limit reached",
                error_code="LIKE_LIMIT_REACHED",
                status_code=429
            )
        
        url = f"{InstagramConfig.BASE_URL}/web/likes/{media_id}/like/"
        response, status_code = self._make_request('POST', url)
        
        if status_code == 200:
            self.session.record_action('like')
            
        return response, status_code
    
    def comment_post(self, media_id: str, comment_text: str) -> Tuple[Dict, int]:
        """Comments on a post on Instagram."""
        if not self.session.can_perform_action('comment'):
            return APIResponse.error(
                "Daily comment limit reached",
                error_code="COMMENT_LIMIT_REACHED",
                status_code=429
            )
        
        url = f"{InstagramConfig.BASE_URL}/web/comments/{media_id}/add/"
        data = {'comment_text': comment_text}
        response, status_code = self._make_request('POST', url, data=data)
        
        if status_code == 200:
            self.session.record_action('comment')
            
        return response, status_code
    
    def get_user_info(self, username: str) -> Tuple[Dict, int]:
        """Gets information about a user."""
        url = f"{InstagramConfig.BASE_URL}/{username}/?__a=1"
        return self._make_request('GET', url)
    
    def get_post_info(self, shortcode: str) -> Tuple[Dict, int]:
        """Gets information about a post."""
        url = f"{InstagramConfig.BASE_URL}/p/{shortcode}/?__a=1"
        return self._make_request('GET', url)
    
    def logout(self) -> None:
        """Logs out and invalidates the session."""
        try:
            self._make_request('POST', InstagramConfig.LOGOUT_URL)
        finally:
            InstagramSessionManager.invalidate_session(self.username)
            self.session = None
