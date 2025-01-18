"""
Configurazione dei test per l'applicazione.
"""

import pytest
from datetime import datetime, timezone, timedelta
from flask import Flask
from flask.testing import FlaskClient
from src.backend import create_app
from src.backend.models import db
from src.backend.models.models import Account
from src.backend.auth.password import hash_password

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app('testing')
    
    # Configure JWT for testing
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLOCKLIST_ENABLED'] = True
    app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = Account(
            username='testuser',
            email='test@example.com',
            password_hash=hash_password('password123'),
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': 'password123'
        }

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    token = response.json['data']['access_token']
    return {'Authorization': f'Bearer {token}'}