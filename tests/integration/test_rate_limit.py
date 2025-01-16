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
    # Crea un account di test con nome univoco
    password = 'Password123!'  # Password più complessa
    print(f"Original password: {password}")
    print(f"Password type: {type(password)}")
    print(f"Password contains digits: {[c for c in password if c.isdigit()]}")
    print(f"Password contains uppercase: {[c for c in password if c.isupper()]}")
    print(f"Password contains lowercase: {[c for c in password if c.islower()]}")
    print(f"Password length: {len(password)}")
    
    register_data = {
        'username': f'testuser_{int(time.time())}',  # Nome utente univoco
        'password': password,
        'email': f'test_{int(time.time())}@example.com'  # Email univoca
    }
    print(f"Sending registration data: {register_data}")  # Debug print
    
    # Verifica che la password sia stata impostata correttamente nei dati
    assert register_data['password'] == password
    assert isinstance(register_data['password'], str)
    assert any(c.isdigit() for c in register_data['password']), "La password deve contenere numeri"
    
    # Verifica manualmente la password
    from src.backend.middleware.auth import validate_password
    is_valid, message = validate_password(register_data['password'])
    print(f"Manual password validation: valid={is_valid}, message={message}")
    
    response = client.post('/api/auth/register', json=register_data)
    print(f"Registration response: {response.data.decode()}")  # Log della risposta

    assert response.status_code == 201, f"Registration failed: {response.data.decode()}"

    # Usa le credenziali corrette per il test
    login_data = {
        'username': register_data['username'],
        'password': password  # La stessa password
    }

    # Esegue 5 richieste (raggiunge il limite)
    for i in range(5):
        response = client.post('/api/auth/login', json=login_data)
        print(f"Login attempt {i+1} response: {response.data.decode()}")  # Log della risposta
        if i < 4:  # Le prime 4 richieste dovrebbero avere successo
            assert response.status_code == 200
        else:  # La quinta richiesta dovrebbe essere limitata
            assert response.status_code == 429

    # Aspetta che il rate limit si resetti (1 minuto)
    time.sleep(60)

    # Prova una nuova richiesta dopo il reset
    response = client.post('/api/auth/login', json=login_data)
    print(f"Final login response: {response.data.decode()}")  # Log della risposta
    assert response.status_code == 200

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