import pytest
import time
from flask import current_app

def test_login_rate_limit(client):
    """Test rate limit per il login"""
    # Dati di test
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    
    # Esegue 6 richieste (il limite è 5 per minuto)
    responses = []
    for _ in range(6):
        response = client.post(
            '/api/auth/login',
            json=data
        )
        responses.append(response)

    # Le prime 5 richieste dovrebbero restituire 401 (credenziali non valide)
    for response in responses[:5]:
        assert response.status_code == 401
        
    # La sesta richiesta dovrebbe essere bloccata dal rate limit
    assert responses[5].status_code == 429
    response_data = responses[5].get_json()
    assert response_data['success'] is False
    assert 'rate limit' in response_data['message'].lower()

def test_register_rate_limit(client):
    """Test rate limit per la registrazione"""
    # Dati di test
    data = {
        'username': 'newuser',
        'password': 'Password123!',
        'email': 'test@example.com'
    }
    
    # Esegue 6 richieste
    responses = []
    for i in range(6):
        data['email'] = f'test{i}@example.com'  # Email diverse per evitare errori di duplicazione
        data['username'] = f'newuser{i}'  # Username diversi
        response = client.post(
            '/api/auth/register',
            json=data
        )
        responses.append(response)

    # Le prime 5 richieste dovrebbero essere processate
    for response in responses[:5]:
        assert response.status_code in [201, 400]  # 201 Created o 400 se validation error
        
    # La sesta richiesta dovrebbe essere bloccata dal rate limit
    assert responses[5].status_code == 429
    response_data = responses[5].get_json()
    assert response_data['success'] is False
    assert 'rate limit' in response_data['message'].lower()