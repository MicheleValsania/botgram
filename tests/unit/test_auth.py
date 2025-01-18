"""
Test per le funzionalità di autenticazione.
"""

import pytest
import json
from flask_login import current_user
from src.backend.models.models import Account, db
from src.backend.auth.password import hash_password, verify_password, validate_password
from src.backend.auth.auth_manager import generate_auth_tokens

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up the database before each test."""
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()

def test_password_functions():
    """Test delle funzioni di gestione password."""
    # Test hash e verifica
    password = "Test123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
    
    # Test validazione
    valid, _ = validate_password("Test123!")
    assert valid
    
    invalid, msg = validate_password("weak")
    assert not invalid
    assert "almeno 8 caratteri" in msg

def test_token_generation(test_account):
    """Test della generazione dei token."""
    tokens = generate_auth_tokens(test_account.id)
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens
    assert tokens['token_type'] == 'bearer'

def test_register(client, app):
    """Test della registrazione utente."""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']
    assert data['data']['user']['username'] == 'testuser'
    assert data['data']['user']['email'] == 'test@example.com'
    
    # Verifica che l'utente sia stato creato nel database
    with app.app_context():
        user = Account.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert verify_password('Test123!', user.password_hash)

def test_register_validation(client):
    """Test della validazione durante la registrazione."""
    # Test password debole
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'weak'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "password" in data['message'].lower()
    
    # Test email invalida
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'invalid',
        'password': 'Test123!'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "email" in data['message'].lower()

def test_login(client, app):
    """Test del login."""
    # Crea un utente
    user = Account(
        username='testuser',
        email='test@example.com',
        password_hash=hash_password('Test123!'),
        is_active=True
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    
    # Test login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']

def test_protected_routes(client, auth_headers):
    """Test delle route protette."""
    # Test senza token
    response = client.get('/api/protected')
    assert response.status_code == 401
    
    # Test con token
    response = client.get('/api/protected', headers=auth_headers)
    assert response.status_code == 200
    
    # Test con token invalido
    invalid_headers = {
        'Authorization': 'Bearer invalid',
        'Content-Type': 'application/json'
    }
    response = client.get('/api/protected', headers=invalid_headers)
    assert response.status_code == 401

def test_refresh_token(client, auth_headers):
    """Test del refresh token."""
    response = client.post('/api/auth/refresh', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data['data']
    
    # Test con token invalido
    invalid_headers = {
        'Authorization': 'Bearer invalid',
        'Content-Type': 'application/json'
    }
    response = client.post('/api/auth/refresh', headers=invalid_headers)
    assert response.status_code == 401
