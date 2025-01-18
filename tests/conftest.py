"""
Configurazione dei test per l'applicazione.
"""

import pytest
from src.backend import create_app
from src.backend.models import db
from src.backend.models.models import Account
from src.backend.auth.password import hash_password
from src.backend.auth.auth_manager import generate_auth_tokens
from src.backend.middleware.rate_limit import RateLimiter

@pytest.fixture(scope='session')
def app():
    """Crea e configura una nuova istanza dell'app per testing."""
    _app = create_app('testing')
    
    # Crea un contesto dell'applicazione
    with _app.app_context():
        # Inizializza il Rate Limiter
        RateLimiter.init_app(_app)
        
        # Crea le tabelle del database
        db.create_all()
        yield _app
        # Pulisce il database dopo i test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Un client di test per l'app."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Crea una nuova sessione del database per un test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        session = db.session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def test_account(app, db_session):
    """Crea un account di test per testing l'autenticazione."""
    account = Account(
        username='test_user',
        email='test@example.com',
        password_hash=hash_password('Test123!'),
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    
    return account

@pytest.fixture
def auth_headers(test_account):
    """Crea header di autenticazione per testing le rotte protette."""
    tokens = generate_auth_tokens(test_account.id)
    return {
        'Authorization': f'Bearer {tokens["access_token"]}',
        'Content-Type': 'application/json'
    }

@pytest.fixture(autouse=True)
def reset_rate_limits(app):
    """Resetta i limiti di velocità tra i test."""
    with app.app_context():
        limiter = RateLimiter.get_instance()
        yield
        try:
            limiter.reset()
        except Exception as e:
            app.logger.warning(f"Failed to reset rate limiter: {e}")