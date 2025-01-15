import pytest
import time
from flask import current_app
from datetime import datetime
from src.backend.middleware.rate_limit import RateLimiter
from src.backend.middleware.response import APIResponse

def test_login_rate_limit(client):
    """Verifica il rate limit sulle richieste di login"""
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    
    responses = []
    for _ in range(6):
        response = client.post('/api/auth/login', json=data)
        responses.append(response)

    for response in responses[:5]:
        assert response.status_code == 401
        
    assert responses[5].status_code == 429
    assert 'rate limit exceeded' in responses[5].get_json()['message'].lower()

@pytest.mark.timeout(70)
def test_api_endpoint_rate_limit(client, auth_headers):
    """Verifica il rate limit sugli endpoint API generici"""
    responses = []
    for _ in range(11):
        response = client.get('/api/auth/me', headers=auth_headers)
        responses.append(response)

    for response in responses[:10]:
        assert response.status_code == 200
        
    assert responses[10].status_code == 429

@pytest.mark.timeout(70)
def test_instagram_endpoint_rate_limit(client, auth_headers):
    """Verifica il rate limit sugli endpoint Instagram"""
    responses = []
    for _ in range(61):
        response = client.post('/api/instagram/action', 
                             headers=auth_headers,
                             json={'type': 'like', 'media_id': '123'})
        responses.append(response)

    for response in responses[:60]:
        assert response.status_code in [200, 404]
        
    assert responses[60].status_code == 429

@pytest.mark.timeout(35)
@pytest.mark.timeout(70)  # Aumentiamo il timeout a 70 secondi
def test_rate_limit_reset(client):
    """Verifica che il rate limit si resetti correttamente"""
    data = {'username': 'testuser', 'password': 'wrongpass'}
    
    # Esegue 5 richieste (raggiunge il limite)
    for _ in range(5):
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 401

    # La sesta richiesta dovrebbe essere bloccata
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 429

    # Aspetta che il rate limit si resetti (62 secondi per sicurezza)
    time.sleep(62)  # Aumentiamo il tempo di attesa oltre il minuto per sicurezza

    # Ora dovrebbe accettare nuove richieste
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401  # Torna a dare errore di credenziali
@pytest.mark.timeout(70)
def test_register_rate_limit(client):
    """Test rate limit per la registrazione"""
    data = {
        'username': 'newuser',
        'password': 'Password123!',
        'email': 'test@example.com'
    }
    
    responses = []
    for i in range(6):
        data['email'] = f'test{i}@example.com'
        data['username'] = f'newuser{i}'
        response = client.post('/api/auth/register', json=data)
        responses.append(response)

    for response in responses[:5]:
        assert response.status_code in [201, 400]
        
    assert responses[5].status_code == 429
    response_data = responses[5].get_json()
    assert response_data['success'] is False
    assert 'rate limit' in response_data['message'].lower()

@pytest.mark.timeout(70)
def test_different_endpoints_rate_limits(client, auth_headers):
    """Verifica che i rate limit siano indipendenti per endpoint diversi"""
    for _ in range(5):
        client.post('/api/auth/login', 
                   json={'username': 'test', 'password': 'wrong'})

    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200