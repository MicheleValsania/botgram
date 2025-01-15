import pytest
from datetime import datetime, timedelta
from src.backend.models.models import Account, Configuration, InteractionLog
from src.backend.config.database import db

def test_concurrent_configuration_updates(client, auth_headers):
    """Test aggiornamenti concorrenti della configurazione"""
    # Crea due configurazioni diverse
    config1 = {
        'daily_like_limit': 100,
        'daily_follow_limit': 50
    }
    
    config2 = {
        'daily_like_limit': 200,
        'daily_follow_limit': 75
    }
    
    # Invia le richieste quasi simultaneamente
    response1 = client.put('/api/config/', json=config1, headers=auth_headers)
    response2 = client.put('/api/config/', json=config2, headers=auth_headers)
    
    # Verifica che una delle richieste abbia successo e l'altra fallisca
    assert (response1.status_code == 200 and response2.status_code == 409) or \
           (response1.status_code == 409 and response2.status_code == 200)

def test_rate_limit_reset(client, auth_headers):
    """Test reset dei rate limit alla mezzanotte"""
    # Simula richieste fino al limite
    for _ in range(5):
        response = client.post('/api/auth/login', 
                             json={'username': 'test', 'password': 'test'})
    
    # Verifica che il rate limit sia stato raggiunto
    assert response.status_code == 429
    
    # Simula il passaggio della mezzanotte
    # Nota: questo richiede modifiche al rate limiter per supportare il test
    time_travel_to_midnight()
    
    # Verifica che il rate limit sia stato resettato
    response = client.post('/api/auth/login', 
                          json={'username': 'test', 'password': 'test'})
    assert response.status_code == 200

def test_interaction_limits_edge_cases(client, auth_headers):
    """Test casi limite per le interazioni"""
    # Test limite esatto
    for _ in range(50):  # daily_like_limit
        response = client.post('/api/interactions/', 
                             json={'type': 'like', 'target_id': 'test'},
                             headers=auth_headers)
        assert response.status_code in [200, 429]
    
    # Verifica che la richiesta successiva fallisca
    response = client.post('/api/interactions/', 
                          json={'type': 'like', 'target_id': 'test'},
                          headers=auth_headers)
    assert response.status_code == 429

def test_error_handling_edge_cases(client, auth_headers):
    """Test gestione errori in casi limite"""
    # Test payload JSON malformato
    response = client.post('/api/interactions/', 
                          data='{"malformed: json}',
                          headers={**auth_headers, 'Content-Type': 'application/json'})
    assert response.status_code == 400
    
    # Test header di autenticazione malformato
    response = client.get('/api/interactions/', 
                         headers={'Authorization': 'malformed_token'})
    assert response.status_code == 401
    
    # Test richiesta con content-type errato
    response = client.post('/api/interactions/', 
                          data='not_json',
                          headers={**auth_headers, 'Content-Type': 'text/plain'})
    assert response.status_code == 415

def test_database_constraints(app):
    """Test vincoli del database in casi limite"""
    with app.app_context():
        # Test username duplicato
        account1 = Account(
            username='test_user',
            email='test1@example.com',
            password_hash='hash1'
        )
        account2 = Account(
            username='test_user',  # Stesso username
            email='test2@example.com',
            password_hash='hash2'
        )
        
        db.session.add(account1)
        db.session.commit()
        
        db.session.add(account2)
        with pytest.raises(Exception):  # Dovrebbe sollevare un'eccezione di unicità
            db.session.commit()
        
        db.session.rollback()

def test_long_running_operations(client, auth_headers):
    """Test operazioni di lunga durata"""
    # Simula un'operazione che richiede molto tempo
    response = client.post('/api/interactions/batch', 
                          json={'actions': ['like'] * 100},
                          headers=auth_headers)
    
    assert response.status_code == 202  # Accepted
    assert 'task_id' in response.json['data']
    
    # Verifica lo stato dell'operazione
    task_id = response.json['data']['task_id']
    response = client.get(f'/api/interactions/batch/{task_id}', 
                         headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['data']['status'] in ['pending', 'processing', 'completed']

# Utility per i test
def time_travel_to_midnight():
    """Simula il passaggio del tempo fino alla mezzanotte"""
    # Implementazione dipendente dal rate limiter usato
    pass