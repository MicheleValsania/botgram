import os
import sys
import pytest
from flask import Flask
from flask.testing import FlaskClient
from typing import Generator, Any
from src.backend.models.models import Account, Configuration, db
from src.backend.middleware.auth import generate_token, hash_password

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def app() -> Flask:
    """Create and configure a Flask application for testing."""
    from src.backend.app import create_app
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Initialize extensions
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a Flask test client."""
    return app.test_client()

@pytest.fixture
def test_user(app: Flask) -> Account:
    """Create a test user in the database."""
    with app.app_context():
        user = Account(
            username='test_user',
            email='test@example.com',
            password_hash=hash_password('TestPass123'),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(test_user: Account) -> dict:
    """Generate authentication headers for test user."""
    token = generate_token(test_user.id)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_config(app: Flask, test_user: Account) -> Configuration:
    """Create a test configuration in the database."""
    with app.app_context():
        config = Configuration(
            account_id=test_user.id,
            daily_like_limit=50,
            daily_follow_limit=20,
            daily_unfollow_limit=10,
            min_delay=2.0,
            max_delay=5.0,
            target_hashtags=['test', 'python'],
            blacklisted_users=['blocked_user'],
            is_active=True
        )
        db.session.add(config)
        db.session.commit()
        return config

# Mock Instagram Session for bot testing
class MockInstagramSession:
    def __init__(self, *args, **kwargs):
        self.logged_in = False
        self.actions = []
    
    async def login(self, password: str) -> bool:
        self.logged_in = True
        return True
    
    async def like_media(self, media_id: str) -> bool:
        self.actions.append(('like', media_id))
        return True
    
    async def follow_user(self, user_id: str) -> bool:
        self.actions.append(('follow', user_id))
        return True
    
    async def close(self) -> None:
        self.logged_in = False

@pytest.fixture
def mock_instagram_session(monkeypatch):
    """Provide a mock Instagram session for bot testing."""
    def mock_init(*args, **kwargs):
        return MockInstagramSession(*args, **kwargs)
    
    monkeypatch.setattr('src.backend.bot.session.InstagramSession', mock_init)
    return MockInstagramSession