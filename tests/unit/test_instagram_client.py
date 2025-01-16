"""
Unit tests for Instagram client.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException

from src.backend.instagram.client import InstagramClient
from src.backend.instagram.session import InstagramSession, InstagramSessionManager
from src.backend.config import InstagramConfig

@pytest.fixture
def mock_session():
    """Fixture for mock Instagram session."""
    session = Mock(spec=InstagramSession)
    session.username = 'testuser'
    session.cookies = {'sessionid': 'abc123'}
    session.user_agent = InstagramConfig.DEFAULT_USER_AGENT
    session.is_valid = True
    session.can_perform_action.return_value = True
    return session

@pytest.fixture
def mock_requests_session():
    """Fixture for mock requests session."""
    with patch('requests.Session') as mock_session:
        session = MagicMock()
        mock_session.return_value = session
        yield session

@pytest.fixture
def instagram_client(mock_session, mock_requests_session):
    """Fixture for Instagram client."""
    return InstagramClient('testuser', mock_session)

class TestInstagramClient:
    """Test cases for InstagramClient class."""
    
    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        client = InstagramClient('testuser', mock_session)
        assert client.username == 'testuser'
        assert client.session is mock_session
    
    def test_client_initialization_no_session(self):
        """Test client initialization with no valid session."""
        with patch('src.backend.instagram.session.InstagramSessionManager.get_session', return_value=None):
            with pytest.raises(ValueError, match='No valid session found'):
                InstagramClient('testuser')
    
    def test_follow_user(self, instagram_client, mock_requests_session):
        """Test follow user functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.request.return_value = mock_response
        
        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 200
        assert response['data']['status'] == 'ok'
        
        # Verify request was made correctly
        mock_requests_session.request.assert_called_with(
            method='POST',
            url=f"{InstagramConfig.BASE_URL}/web/friendships/user123/follow/",
            data=None,
            params=None,
            timeout=30
        )
    
    def test_like_post(self, instagram_client, mock_requests_session):
        """Test like post functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.request.return_value = mock_response
        
        response, status_code = instagram_client.like_post('media123')
        assert status_code == 200
        assert response['data']['status'] == 'ok'
        
        # Verify request was made correctly
        mock_requests_session.request.assert_called_with(
            method='POST',
            url=f"{InstagramConfig.BASE_URL}/web/likes/media123/like/",
            data=None,
            params=None,
            timeout=30
        )
    
    def test_comment_post(self, instagram_client, mock_requests_session):
        """Test comment post functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.request.return_value = mock_response
        
        comment_text = "Great post!"
        response, status_code = instagram_client.comment_post('media123', comment_text)
        assert status_code == 200
        assert response['data']['status'] == 'ok'
        
        # Verify request was made correctly
        mock_requests_session.request.assert_called_with(
            method='POST',
            url=f"{InstagramConfig.BASE_URL}/web/comments/media123/add/",
            data={'comment_text': comment_text},
            params=None,
            timeout=30
        )
    
    def test_rate_limit_handling(self, instagram_client, mock_requests_session):
        """Test rate limit handling."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_requests_session.request.return_value = mock_response
        
        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 429
        assert response['error_code'] == 'RATE_LIMIT_EXCEEDED'
    
    def test_error_handling(self, instagram_client, mock_requests_session):
        """Test error handling."""
        # Mock network error
        mock_requests_session.request.side_effect = RequestException("Network error")
        
        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 500
        assert response['error_code'] == 'REQUEST_FAILED'
    
    def test_invalid_session(self, instagram_client, mock_session):
        """Test behavior with invalid session."""
        mock_session.is_valid = False
        
        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 401
        assert response['error_code'] == 'INVALID_SESSION'
    
    def test_logout(self, instagram_client, mock_requests_session, mock_session):
        """Test logout functionality."""
        # Mock successful logout response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_session.request.return_value = mock_response
        
        instagram_client.logout()
        
        # Verify logout request was made
        mock_requests_session.request.assert_called_with(
            method='POST',
            url=InstagramConfig.LOGOUT_URL,
            data=None,
            params=None,
            timeout=30
        )
        
        # Verify session was invalidated
        assert instagram_client.session is None
