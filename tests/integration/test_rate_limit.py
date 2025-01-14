import pytest
import time
from flask import current_app
from datetime import datetime

def test_login_rate_limit(client):
    """Verifica il rate limit sulle richieste di login"""
    # Preparazione dei dati di test
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    
    # Esegue 6 richieste (il limite è 5 per minuto)
    responses = []
    for _ in range(6):
        response = client.post('/api/auth/login', json=data)
        responses.append(response)

    # Verifica che le prime 5 richieste siano state elaborate (401 per credenziali errate)
    for response in responses[:5]:
        assert response.status_code == 401
        
    # La sesta richiesta dovrebbe essere bloccata dal rate limit
    assert responses[5].status_code == 429
    assert 'rate limit exceeded' in responses[5].get_json()['message'].lower()

def test_api_endpoint_rate_limit(client, auth_headers):
    """Verifica il rate limit sugli endpoint API generici"""
    # Esegue 11 richieste (il limite è 10 per minuto)
    responses = []
    for _ in range(11):
        response = client.get('/api/auth/me', headers=auth_headers)
        responses.append(response)

    # Le prime 10 richieste dovrebbero avere successo
    for response in responses[:10]:
        assert response.status_code == 200
        
    # L'undicesima richiesta dovrebbe essere bloccata
    assert responses[10].status_code == 429

def test_instagram_endpoint_rate_limit(client, auth_headers):
    """Verifica il rate limit sugli endpoint Instagram"""
    # Simula 61 richieste Instagram (limite 60 per ora)
    responses = []
    for _ in range(61):
        response = client.post('/api/instagram/action', 
                             headers=auth_headers,
                             json={'type': 'like', 'media_id': '123'})
        responses.append(response)

    # Prime 60 richieste dovrebbero essere processate
    for response in responses[:60]:
        assert response.status_code in [200, 404]  # 404 è ok perché stiamo solo testando il rate limit
        
    # La 61esima richiesta dovrebbe essere bloccata
    assert responses[60].status_code == 429

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

    # Aspetta che il rate limit si resetti (61 secondi per sicurezza)
    time.sleep(61)

    # Ora dovrebbe accettare nuove richieste
    response = client.post('/api/auth/login', json=data)
    assert response.status_code == 401  # Torna a dare errore di credenziali invece che di rate limit

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
        response = client.post('/api/auth/register', json=data)
        responses.append(response)

    # Le prime 5 richieste dovrebbero essere processate
    for response in responses[:5]:
        assert response.status_code in [201, 400]  # 201 Created o 400 se validation error
        
    # La sesta richiesta dovrebbe essere bloccata dal rate limit
    assert responses[5].status_code == 429
    response_data = responses[5].get_json()
    assert response_data['success'] is False
    assert 'rate limit' in response_data['message'].lower()

def test_different_endpoints_rate_limits(client, auth_headers):
    """Verifica che i rate limit siano indipendenti per endpoint diversi"""
    # Esaurisce il rate limit su login
    for _ in range(5):
        client.post('/api/auth/login', 
                   json={'username': 'test', 'password': 'wrong'})

    # Verifica che altri endpoint siano ancora accessibili
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200  # Dovrebbe funzionare perché ha un rate limit separato