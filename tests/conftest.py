import pytest
from src.backend import create_app
from src.backend.config.database import db
from src.backend.models.models import Account
from src.backend.middleware.auth import hash_password, generate_token

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
        
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def test_account(app, db_session):
    """Create a test account that remains in session"""
    account = Account(
        username='testuser',
        password_hash=hash_password('Password123!'),
        email='test@example.com',
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    
    # Query back the account to ensure it's attached to the session
    account = Account.query.filter_by(username='testuser').first()
    return account

@pytest.fixture
def auth_headers(test_account):
    """Create authentication headers for testing protected routes"""
    token = generate_token(test_account.id)
    return {'Authorization': f'Bearer {token}'}