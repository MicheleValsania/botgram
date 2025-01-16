import pytest
import json
from flask import url_for
from src.backend.middleware.response import APIResponse
from src.backend.models.models import Account
from src.backend.config.database import db

def test_json_decode_error(client):
    """Test per JSON malformato"""
    response = client.post('/api/auth/login',
                          data='{malformed: json}',
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error_code'] == 'INVALID_JSON'
    assert not data['success']

def test_bad_request_error(client):
    """Test per richiesta malformata"""
    # Mancano campi obbligatori
    response = client.post('/api/auth/login',
                          json={'username': 'test'})  # manca password
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error_code'] == 'VALIDATION_ERROR'
    assert not data['success']

def test_unauthorized_error(client):
    """Test per richiesta non autorizzata"""
    response = client.get('/api/interactions/')  # senza token
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error_code'] == 'UNAUTHORIZED'
    assert not data['success']


def test_forbidden_error(client, auth_headers):
    """Test per accesso negato"""
    # Simuliamo un account disattivato
    with client.application.app_context():
        account = Account.query.first()
        print(f"Initial account state: {account.is_active}")
        if account:
            account.is_active = False
            db.session.commit()
            # Verifica dopo il commit
            db.session.refresh(account)
            print(f"Account state after commit: {account.is_active}")
            # Doppio check diretto dal database
            check_account = Account.query.get(account.id)
            print(f"Account state from fresh query: {check_account.is_active}")
    
    response = client.get('/api/interactions/', headers=auth_headers)
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data.decode()}")
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error_code'] == 'FORBIDDEN'
    assert not data['success']
def test_not_found_error(client, auth_headers):
    """Test per risorsa non trovata"""
    response = client.get('/api/not/exists', headers=auth_headers)
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error_code'] == 'NOT_FOUND'
    assert not data['success']

def test_internal_server_error(client, auth_headers):
    """Test per errore interno del server"""
    response = client.get('/api/test-internal-error', headers=auth_headers)
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error_code'] == 'INTERNAL_ERROR'
    assert not data['success']

def test_production_error_message(client):
    """Test per messaggi di errore in produzione"""
    app = client.application
    app.config['ENV'] = 'production'
    
    response = client.post('/api/auth/login',
                          data='{malformed: json}',
                          content_type='application/json')
    
    data = json.loads(response.data)
    assert 'interno' in data['message'].lower()  # Messaggio generico in produzione
    app.config['ENV'] = 'development'  # Ripristina l'ambiente