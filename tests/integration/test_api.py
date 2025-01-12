import pytest
import json
from src.backend.models.models import Account, Configuration

def test_register_endpoint(client):
    """Test user registration endpoint."""
    # Test successful registration
    response = client.post('/api/auth/register', json={
        'username': 'new_user',
        'email': 'new@example.com',
        'password': 'SecurePass123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'access_token' in data['data']
    
    # Test duplicate username
    response = client.post('/api/auth/register', json={
        'username': 'new_user',
        'email': 'another@example.com',
        'password': 'SecurePass123'
    })
    assert response.status_code == 400
    
    # Test invalid password
    response = client.post('/api/auth/register', json={
        'username': 'another_user',
        'email': 'valid@example.com',
        'password': 'weak'
    })
    assert response.status_code == 400

def test_login_endpoint(client, test_user):
    """Test login endpoint."""
    # Test successful login
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'TestPass123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'access_token' in data['data']
    
    # Test invalid credentials
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'WrongPass123'
    })
    assert response.status_code == 401

def test_protected_endpoints(client, auth_headers, test_user):
    """Test endpoints that require authentication."""
    # Test getting user profile
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['username'] == test_user.username
    
    # Test without auth headers
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_configuration_endpoints(client, auth_headers, test_config):
    """Test configuration management endpoints."""
    # Test get configuration
    response = client.get('/api/config/', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['daily_like_limit'] == test_config.daily_like_limit
    
    # Test update configuration
    new_config = {
        'daily_like_limit': 60,
        'daily_follow_limit': 25,
        'target_hashtags': ['updated', 'tags']
    }
    response = client.put('/api/config/', 
                         headers=auth_headers,
                         json=new_config)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['daily_like_limit'] == 60

def test_interaction_endpoints(client, auth_headers, test_user):
    """Test interaction logging endpoints."""
    # Test create interaction
    interaction_data = {
        'interaction_type': 'like',
        'target_username': 'target_user',
        'status': 'success'
    }
    response = client.post('/api/interactions/',
                          headers=auth_headers,
                          json=interaction_data)
    assert response.status_code == 201
    
    # Test get interactions
    response = client.get('/api/interactions/', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) > 0

def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # Make multiple rapid requests to a rate-limited endpoint
    for _ in range(5):
        response = client.post('/api/auth/login', json={
            'username': 'test_user',
            'password': 'TestPass123'
        })
    
    # The next request should be rate limited
    response = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'TestPass123'
    })
    assert response.status_code == 429

def test_error_handling(client, auth_headers):
    """Test error handling for various scenarios."""
    # Test 404 Not Found
    response = client.get('/api/nonexistent', headers=auth_headers)
    assert response.status_code == 404
    
    # Test invalid JSON
    response = client.post('/api/auth/register', 
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test validation error
    response = client.post('/api/auth/register', json={
        'username': 'u',  # Too short
        'email': 'invalid-email',
        'password': 'short'
    })
    assert response.status_code == 400