import json
import pytest
from src.backend.models.models import Account
from src.backend.config.database import db

def test_register_success(client):
    """Test successful registration"""
    data = {
        'username': 'newuser',
        'password': 'Password123!',
        'email': 'newuser@example.com'
    }
    
    # Print available routes before the request
    print("\nAvailable routes before request:")
    for rule in client.application.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule} {rule.methods}")
    
    response = client.post('/api/auth/register', json=data)
    
    # Print response details
    print(f"\nResponse status: {response.status_code}")
    print(f"Response data: {response.data.decode()}")
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['success'] is True
    assert 'access_token' in response_data['data']
    assert 'user_id' in response_data['data']
    
    # Verify the account was created in the database
    created_account = Account.query.filter_by(username='newuser').first()
    assert created_account is not None
    assert created_account.email == 'newuser@example.com'

def test_register_duplicate_username(client):
    """Test registration with existing username"""
    # Create initial user
    data = {
        'username': 'testuser',
        'password': 'Password123!',
        'email': 'test@example.com'
    }
    client.post('/api/auth/register', json=data)
    
    # Try to register with same username
    data['email'] = 'different@example.com'
    response = client.post('/api/auth/register', json=data)
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'Username già in uso' in response_data['message']

def test_register_invalid_password(client):
    """Test registration with invalid password"""
    data = {
        'username': 'newuser',
        'password': 'weak',  # Too short and missing requirements
        'email': 'test@example.com'
    }
    response = client.post('/api/auth/register', json=data)
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'password' in response_data['message'].lower()