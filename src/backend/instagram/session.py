"""
Instagram session management module.
Handles authentication, session persistence, and rate limiting for Instagram interactions.
"""
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..middleware.rate_limit import RateLimiter
from ..config import InstagramConfig

logger = logging.getLogger(__name__)

@dataclass
class InstagramSession:
    """Represents an Instagram session with authentication and rate limiting."""
    username: str
    session_id: str
    created_at: datetime
    last_action: datetime
    rate_limits: Dict[str, int]
    cookies: Dict[str, str]
    user_agent: str
    is_valid: bool = True
    
    @classmethod
    def create(cls, username: str, session_id: str, cookies: Dict[str, str], 
               user_agent: str) -> 'InstagramSession':
        """Creates a new Instagram session."""
        now = datetime.utcnow()
        return cls(
            username=username,
            session_id=session_id,
            created_at=now,
            last_action=now,
            rate_limits={
                'follow': InstagramConfig.FOLLOW_LIMIT_PER_DAY,
                'like': InstagramConfig.LIKE_LIMIT_PER_DAY,
                'comment': InstagramConfig.COMMENT_LIMIT_PER_DAY
            },
            cookies=cookies,
            user_agent=user_agent
        )
    
    def update_last_action(self) -> None:
        """Updates the last action timestamp."""
        self.last_action = datetime.utcnow()
    
    def is_session_expired(self) -> bool:
        """Checks if the session has expired."""
        return (datetime.utcnow() - self.last_action) > timedelta(
            hours=InstagramConfig.SESSION_EXPIRY_HOURS
        )
    
    def can_perform_action(self, action_type: str) -> bool:
        """Checks if an action can be performed based on rate limits."""
        if action_type not in self.rate_limits:
            logger.warning(f"Unknown action type: {action_type}")
            return False
            
        return self.rate_limits[action_type] > 0
    
    def record_action(self, action_type: str) -> None:
        """Records an action and updates rate limits."""
        if action_type in self.rate_limits:
            self.rate_limits[action_type] -= 1
            self.update_last_action()
            
    def get_remaining_limits(self) -> Dict[str, int]:
        """Returns the remaining limits for all action types."""
        return self.rate_limits.copy()

class InstagramSessionManager:
    """Manages Instagram sessions and their lifecycle."""
    _sessions: Dict[str, InstagramSession] = {}
    
    @classmethod
    def create_session(cls, username: str, session_id: str, 
                      cookies: Dict[str, str], user_agent: str) -> InstagramSession:
        """Creates and stores a new Instagram session."""
        session = InstagramSession.create(
            username=username,
            session_id=session_id,
            cookies=cookies,
            user_agent=user_agent
        )
        cls._sessions[username] = session
        logger.info(f"Created new Instagram session for user: {username}")
        return session
    
    @classmethod
    def get_session(cls, username: str) -> Optional[InstagramSession]:
        """Retrieves an active session for a user."""
        session = cls._sessions.get(username)
        if not session:
            return None
            
        if session.is_session_expired():
            logger.info(f"Session expired for user: {username}")
            cls.invalidate_session(username)
            return None
            
        return session
    
    @classmethod
    def invalidate_session(cls, username: str) -> None:
        """Invalidates and removes a user's session."""
        if username in cls._sessions:
            cls._sessions[username].is_valid = False
            del cls._sessions[username]
            logger.info(f"Invalidated session for user: {username}")
    
    @classmethod
    def cleanup_expired_sessions(cls) -> None:
        """Removes all expired sessions."""
        expired_users = [
            username for username, session in cls._sessions.items()
            if session.is_session_expired()
        ]
        for username in expired_users:
            cls.invalidate_session(username)
