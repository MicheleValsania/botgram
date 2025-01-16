"""
Unit tests for Instagram session management.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.backend.instagram.session import InstagramSession, InstagramSessionManager
from src.backend.config import InstagramConfig

@pytest.fixture
def mock_session_data():
    """Fixture for test session data."""
    return {
        'username': 'testuser',
        'session_id': 'test_session_123',
        'cookies': {'sessionid': 'abc123', 'csrftoken': 'xyz789'},
        'user_agent': InstagramConfig.DEFAULT_USER_AGENT
    }

@pytest.fixture
def instagram_session(mock_session_data):
    """Fixture for Instagram session."""
    return InstagramSession.create(**mock_session_data)

class TestInstagramSession:
    """Test cases for InstagramSession class."""
    
    def test_session_creation(self, mock_session_data):
        """Test session creation with valid data."""
        session = InstagramSession.create(**mock_session_data)
        
        assert session.username == mock_session_data['username']
        assert session.session_id == mock_session_data['session_id']
        assert session.cookies == mock_session_data['cookies']
        assert session.user_agent == mock_session_data['user_agent']
        assert session.is_valid is True
        
        # Verify rate limits are set correctly
        assert session.rate_limits['follow'] == InstagramConfig.FOLLOW_LIMIT_PER_DAY
        assert session.rate_limits['like'] == InstagramConfig.LIKE_LIMIT_PER_DAY
        assert session.rate_limits['comment'] == InstagramConfig.COMMENT_LIMIT_PER_DAY
    
    def test_session_expiry(self, instagram_session):
        """Test session expiry logic."""
        # New session should not be expired
        assert not instagram_session.is_session_expired()
        
        # Set last action to more than expiry hours ago
        instagram_session.last_action = datetime.utcnow() - timedelta(
            hours=InstagramConfig.SESSION_EXPIRY_HOURS + 1
        )
        assert instagram_session.is_session_expired()
    
    def test_action_tracking(self, instagram_session):
        """Test action tracking and limits."""
        # Test follow action
        assert instagram_session.can_perform_action('follow')
        initial_follow_limit = instagram_session.rate_limits['follow']
        
        instagram_session.record_action('follow')
        assert instagram_session.rate_limits['follow'] == initial_follow_limit - 1
        
        # Test invalid action type
        assert not instagram_session.can_perform_action('invalid_action')
        
        # Test limit reached
        instagram_session.rate_limits['like'] = 0
        assert not instagram_session.can_perform_action('like')
    
    def test_last_action_update(self, instagram_session):
        """Test last action timestamp update."""
        old_timestamp = instagram_session.last_action
        instagram_session.update_last_action()
        assert instagram_session.last_action > old_timestamp

class TestInstagramSessionManager:
    """Test cases for InstagramSessionManager class."""
    
    def setup_method(self):
        """Setup method to clear sessions before each test."""
        InstagramSessionManager._sessions = {}
    
    def test_session_management(self, mock_session_data):
        """Test session creation and retrieval."""
        # Create new session
        session = InstagramSessionManager.create_session(**mock_session_data)
        assert session.username == mock_session_data['username']
        
        # Retrieve existing session
        retrieved_session = InstagramSessionManager.get_session(mock_session_data['username'])
        assert retrieved_session is session
        
        # Try to get non-existent session
        assert InstagramSessionManager.get_session('nonexistent') is None
    
    def test_session_invalidation(self, mock_session_data):
        """Test session invalidation."""
        session = InstagramSessionManager.create_session(**mock_session_data)
        assert InstagramSessionManager.get_session(mock_session_data['username']) is session
        
        InstagramSessionManager.invalidate_session(mock_session_data['username'])
        assert InstagramSessionManager.get_session(mock_session_data['username']) is None
        assert not session.is_valid
    
    def test_expired_session_cleanup(self, mock_session_data):
        """Test cleanup of expired sessions."""
        session = InstagramSessionManager.create_session(**mock_session_data)
        
        # Make session expired
        session.last_action = datetime.utcnow() - timedelta(
            hours=InstagramConfig.SESSION_EXPIRY_HOURS + 1
        )
        
        InstagramSessionManager.cleanup_expired_sessions()
        assert InstagramSessionManager.get_session(mock_session_data['username']) is None
    
    def test_multiple_sessions(self, mock_session_data):
        """Test handling of multiple sessions."""
        # Create sessions for different users
        session1 = InstagramSessionManager.create_session(**mock_session_data)
        
        user2_data = mock_session_data.copy()
        user2_data['username'] = 'testuser2'
        user2_data['session_id'] = 'test_session_456'
        session2 = InstagramSessionManager.create_session(**user2_data)
        
        # Verify both sessions are stored and retrievable
        assert InstagramSessionManager.get_session(mock_session_data['username']) is session1
        assert InstagramSessionManager.get_session(user2_data['username']) is session2
        
        # Invalidate one session
        InstagramSessionManager.invalidate_session(mock_session_data['username'])
        assert InstagramSessionManager.get_session(mock_session_data['username']) is None
        assert InstagramSessionManager.get_session(user2_data['username']) is session2
