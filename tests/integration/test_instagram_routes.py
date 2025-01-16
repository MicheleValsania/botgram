"""
Integration tests for Instagram routes.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta

from src.backend.app import create_app
from src.backend.config import Config, InstagramConfig
from src.backend.instagram.session import InstagramSessionManager

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key'
    })
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Authentication headers for test requests."""
    return {'Authorization': 'Bearer test_token'}

@pytest.fixture
def mock_session_data():
    """Test session data."""
    return {
        'username': 'testuser',
        'session_id': 'test_session_123',
        'cookies': {'sessionid': 'abc123', 'csrftoken': 'xyz789'},
        'user_agent': InstagramConfig.DEFAULT_USER_AGENT
    }

class TestInstagramRoutes:
    """Test cases for Instagram routes."""
    
    def test_create_session(self, client, auth_headers, mock_session_data):
        """Test session creation endpoint."""
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            response = client.post(
                '/api/instagram/session',
                json=mock_session_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json['success'] is True
            assert response.json['data']['session_created'] is True
            
            # Verify session was created
            session = InstagramSessionManager.get_session(mock_session_data['username'])
            assert session is not None
            assert session.username == mock_session_data['username']
    
    def test_follow_user(self, client, auth_headers):
        """Test follow user endpoint."""
        # Create test session
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            with patch('src.backend.instagram.client.InstagramClient.follow_user') as mock_follow:
                mock_follow.return_value = ({'data': {'status': 'ok'}}, 200)
                
                response = client.post(
                    '/api/instagram/follow',
                    json={
                        'username': 'testuser',
                        'target_user_id': 'user123',
                        'action_type': 'follow'
                    },
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                assert response.json['success'] is True
                assert response.json['data']['status'] == 'ok'
    
    def test_like_post(self, client, auth_headers):
        """Test like post endpoint."""
        # Create test session
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            with patch('src.backend.instagram.client.InstagramClient.like_post') as mock_like:
                mock_like.return_value = ({'data': {'status': 'ok'}}, 200)
                
                response = client.post(
                    '/api/instagram/like',
                    json={
                        'username': 'testuser',
                        'media_id': 'media123',
                        'action_type': 'like'
                    },
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                assert response.json['success'] is True
                assert response.json['data']['status'] == 'ok'
    
    def test_comment_post(self, client, auth_headers):
        """Test comment post endpoint."""
        # Create test session
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            with patch('src.backend.instagram.client.InstagramClient.comment_post') as mock_comment:
                mock_comment.return_value = ({'data': {'status': 'ok'}}, 200)
                
                response = client.post(
                    '/api/instagram/comment',
                    json={
                        'username': 'testuser',
                        'media_id': 'media123',
                        'comment_text': 'Great post!',
                        'action_type': 'comment'
                    },
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                assert response.json['success'] is True
                assert response.json['data']['status'] == 'ok'
    
    def test_end_session(self, client, auth_headers):
        """Test session termination endpoint."""
        # Create test session
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            with patch('src.backend.instagram.client.InstagramClient.logout') as mock_logout:
                response = client.delete(
                    '/api/instagram/session/testuser',
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                assert response.json['success'] is True
                
                # Verify session was invalidated
                assert InstagramSessionManager.get_session('testuser') is None
    
    def test_get_limits(self, client, auth_headers):
        """Test get limits endpoint."""
        # Create test session with specific limits
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        session.rate_limits = {
            'follow': 100,
            'like': 200,
            'comment': 50
        }
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            response = client.get(
                '/api/instagram/limits/testuser',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json['success'] is True
            assert response.json['data']['limits']['follow'] == 100
            assert response.json['data']['limits']['like'] == 200
            assert response.json['data']['limits']['comment'] == 50
    
    def test_rate_limit_exceeded(self, client, auth_headers):
        """Test rate limit handling."""
        # Create test session with exhausted limits
        session = InstagramSessionManager.create_session(
            username='testuser',
            session_id='test123',
            cookies={'sessionid': 'abc123'},
            user_agent=InstagramConfig.DEFAULT_USER_AGENT
        )
        session.rate_limits['follow'] = 0
        
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            response = client.post(
                '/api/instagram/follow',
                json={
                    'username': 'testuser',
                    'target_user_id': 'user123',
                    'action_type': 'follow'
                },
                headers=auth_headers
            )
            
            assert response.status_code == 429
            assert response.json['success'] is False
            assert response.json['error_code'] == 'RATE_LIMIT_EXCEEDED'
    
    def test_invalid_session(self, client, auth_headers):
        """Test handling of invalid session."""
        with patch('src.backend.middleware.auth.verify_token', return_value=True):
            response = client.post(
                '/api/instagram/follow',
                json={
                    'username': 'nonexistent',
                    'target_user_id': 'user123',
                    'action_type': 'follow'
                },
                headers=auth_headers
            )
            
            assert response.status_code == 401
            assert response.json['success'] is False
            assert response.json['error_code'] == 'INVALID_SESSION'
