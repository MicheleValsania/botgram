# tests/integration/test_api.py
import pytest
import json
from src.backend.models.models import Account
from src.backend.config.database import db

def test_register_success(client):
    """Test successful registration"""
    data = {
        'username': 'newuser',
        'password': 'Password123!',
        'email': 'newuser@example.com'
    }
    response = client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    assert 'access_token' in response_data['data']
    assert 'user_id' in response_data['data']

def test_register_duplicate_username(client, test_account):
    """Test registration with existing username"""
    data = {
        'username': 'testuser',  # Stesso username del test_account
        'password': 'Password123!',
        'email': 'different@example.com'
    }
    response = client.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'Username già in uso' in response_data['message']

def test_login_success(client, test_account):
    """Test successful login"""
    data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    assert 'access_token' in response_data['data']

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'Credenziali non valide' in response_data['message']

def test_get_me_authenticated(client, auth_headers):
    """Test getting user profile when authenticated"""
    response = client.get(
        '/api/auth/me',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    assert response_data['data']['username'] == 'testuser'

def test_get_me_no_token(client):
    """Test getting user profile without token"""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'Token mancante' in response_data['message']