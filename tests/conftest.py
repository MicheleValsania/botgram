# tests/conftest.py
import pytest
from src.backend import create_app
from src.backend.config.database import db
from src.backend.models.models import Account
from src.backend.middleware.auth import hash_password, generate_token

@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    app = create_app('testing')  # Usa la nostra funzione create_app invece di Flask(__name__)
    
    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_account(app):
    """Create a test account that remains in session"""
    with app.app_context():
        account = Account(
            username='testuser',
            password_hash=hash_password('password123'),
            email='test@example.com',
            is_active=True
        )
        db.session.add(account)
        db.session.commit()
        
        # Query back the account to ensure it's attached to the session
        account = Account.query.filter_by(username='testuser').first()
        return account

@pytest.fixture
def auth_headers(test_account):
    """Create authentication headers for testing protected routes"""
    token = generate_token(test_account.id)
    return {'Authorization': f'Bearer {token}'}