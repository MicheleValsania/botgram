import pytest
import json
from flask_login import current_user
from src.backend.models.models import Account, db
from src.backend.middleware.auth import verify_password, hash_password

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up the database before each test"""
    with app.app_context():
        db.session.query(Account).delete()
        db.session.commit()

def test_register(client, app):
    """Test della registrazione utente"""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
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
        assert verify_password('TestPassword123', user.password_hash)

def test_register_duplicate_username(client):
    """Test registrazione con username duplicato"""
    # Prima registrazione
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'TestPassword123'
    })
    
    # Seconda registrazione con stesso username
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'TestPassword123'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Username già in uso' in data['message']

def test_login(client, app):
    """Test del login"""
    # Registra un utente
    register_response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })
    register_data = json.loads(register_response.data)
    print(f"Registration response: {register_data}")
    
    # Verifica l'hash della password nel database
    with app.app_context():
        user = Account.query.filter_by(username='testuser').first()
        print(f"User password hash: {user.password_hash}")
        assert verify_password('TestPassword123', user.password_hash)
    
    # Effettua il login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']
    assert data['data']['user']['username'] == 'testuser'
    
    # Verifica che l'utente sia loggato
    with client:
        client.get('/')  # Fa una richiesta per attivare il contesto
        assert current_user.is_authenticated
        assert current_user.username == 'testuser'

def test_login_invalid_credentials(client):
    """Test login con credenziali non valide"""
    # Registra un utente
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })
    
    # Prova il login con password sbagliata
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'WrongPassword123'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Password non valida' in data['message']

def test_logout(client):
    """Test del logout"""
    # Registra e logga un utente
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })
    login_response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    
    # Estrai il token
    data = json.loads(login_response.data)
    token = data['data']['access_token'] if data.get('success', False) else None
    
    if token:
        # Effettua il logout
        response = client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
        
        # Verifica che l'utente sia sloggato
        with client:
            client.get('/')
            assert not current_user.is_authenticated

def test_protected_route(client):
    """Test di una route protetta"""
    # Prova ad accedere senza token
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    
    # Registra e logga un utente
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123'
    })
    login_response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    
    # Estrai il token
    data = json.loads(login_response.data)
    token = data['data']['access_token'] if data.get('success', False) else None
    
    if token:
        # Accedi alla route protetta
        response = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['username'] == 'testuser'

def test_password_validation(client):
    """Test della validazione password"""
    # Password troppo corta
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Short1'
    })
    assert response.status_code == 400
    
    # Password senza maiuscole
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    
    # Password senza minuscole
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'PASSWORD123'
    })
    assert response.status_code == 400
    
    # Password senza numeri
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'PasswordOnly'
    })
    assert response.status_code == 400
