import pytest
from src.backend import create_app
from src.backend.config.database import db
from src.backend.models.models import Account
from src.backend.middleware.auth import hash_password, generate_token
from src.backend.middleware.rate_limit import RateLimiter  # Aggiungi questa importazione
from src.backend.middleware.response import APIResponse    # Aggiungi questa importazione

@pytest.fixture(autouse=True)
def reset_rate_limits(app):
    """Reset rate limits between tests"""
    limiter = RateLimiter.get_instance()
    yield
    try:
        limiter.reset()
    except Exception as e:
        app.logger.warning(f"Failed to reset rate limiter: {e}")

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for testing."""
    _app = create_app('testing')
    
    # Crea un contesto dell'applicazione
    with _app.app_context():
        # Create tables
        db.create_all()
        yield _app
        # Cleanup dopo i test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create a fresh database session for a test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Usiamo direttamente db.session
        session = db.session
        
        # In alternativa, se proprio vogliamo una sessione scoped:
        # session = db.session.registry()
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()
@pytest.fixture
def test_account(app, db_session):
    """Create a test account that remains in session"""
    # Prima cerchiamo se esiste già
    existing = Account.query.filter_by(email='test@example.com').first()
    if existing:
        return existing
        
    account = Account(
        username='testuser',
        password_hash=hash_password('Password123!'),
        email='test@example.com',
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    return account

@pytest.fixture
def auth_headers(test_account):
    """Create authentication headers for testing protected routes"""
    token = generate_token(test_account.id)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture(autouse=True)
def reset_rate_limits(app):
    """Reset dei rate limit dopo ogni test"""
    with app.app_context():
        yield
        limiter = RateLimiter.get_instance()
        if hasattr(limiter, 'reset'):
            limiter.reset()