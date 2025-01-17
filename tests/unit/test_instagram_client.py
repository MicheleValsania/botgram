"""Tests for Instagram client."""
from unittest.mock import Mock, patch, MagicMock
import pytest
from requests.exceptions import RequestException
from src.backend.instagram.client import InstagramClient
from src.backend.instagram.session import InstagramSession
from src.backend.config import InstagramConfig

class TestInstagramClient:
    """Test Instagram client."""

    @pytest.fixture
    def mock_session(self):
        """Mock Instagram session."""
        session = Mock(spec=InstagramSession)
        session.username = 'testuser'
        session.is_valid = True
        session.user_agent = 'test-agent'
        session.cookies = {'sessionid': 'test123'}
        return session

    @pytest.fixture
    def mock_requests_session(self):
        """Mock requests session."""
        with patch('src.backend.instagram.client.requests.request') as mock:
            yield mock

    @pytest.fixture
    def instagram_client(self, mock_session):
        """Fixture for Instagram client."""
        with patch('src.backend.instagram.session.InstagramSessionManager.get_session', return_value=mock_session):
            client = InstagramClient(username='testuser')
            client.session = mock_session
            return client

    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        with patch('src.backend.instagram.session.InstagramSessionManager.get_session', return_value=mock_session):
            client = InstagramClient(username='testuser')
            assert client.username == 'testuser'
            assert client.session == mock_session

    def test_client_initialization_no_session(self):
        """Test client initialization with no valid session."""
        with patch('src.backend.instagram.session.InstagramSessionManager.get_session', return_value=None):
            with pytest.raises(ValueError, match='No valid session found'):
                InstagramClient(username='testuser')

    def test_follow_user(self, instagram_client, mock_requests_session):
        """Test follow user functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.return_value = mock_response

        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 200
        assert response['status'] == 'ok'

    def test_like_post(self, instagram_client, mock_requests_session):
        """Test like post functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.return_value = mock_response

        response, status_code = instagram_client.like_post('media123')
        assert status_code == 200
        assert response['status'] == 'ok'

    def test_comment_post(self, instagram_client, mock_requests_session):
        """Test comment post functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.return_value = mock_response

        comment_text = "Great post!"
        response, status_code = instagram_client.comment_post('media123', comment_text)
        assert status_code == 200
        assert response['status'] == 'ok'

    def test_rate_limit_handling(self, instagram_client, mock_requests_session):
        """Test rate limit handling."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {'error': 'Rate limit exceeded'}
        mock_requests_session.return_value = mock_response

        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 429
        assert response['error'] == 'Rate limit exceeded'

    def test_error_handling(self, instagram_client, mock_requests_session):
        """Test error handling."""
        # Mock network error
        mock_requests_session.side_effect = RequestException("Network error")

        response, status_code = instagram_client.follow_user('user123')
        assert status_code == 500
        assert response['error'] == 'Network error'

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
        mock_response.json.return_value = {'status': 'ok'}
        mock_requests_session.return_value = mock_response

        response, status_code = instagram_client.logout()
        assert status_code == 200
        assert response['status'] == 'ok'

        # Verify logout request was made
        mock_requests_session.assert_called_with(
            method='POST',
            url=InstagramConfig.LOGOUT_URL,
            headers={
                'User-Agent': mock_session.user_agent,
                'Cookie': 'sessionid=test123'
            },
            data=None,
            params=None,
            timeout=30
        )
