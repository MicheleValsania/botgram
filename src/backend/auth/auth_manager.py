"""
Gestione centralizzata dell'autenticazione.
Supporta sia l'autenticazione basata su sessione (Flask-Login) che token (JWT).
"""

from flask_login import LoginManager
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token
)
from datetime import timedelta
from ..models.models import Account
from .password import hash_password, verify_password, validate_password

login_manager = LoginManager()
jwt = JWTManager()

@login_manager.user_loader
def load_user(user_id: int) -> Account:
    """
    Carica un utente dal database per Flask-Login.
    
    Args:
        user_id: ID dell'utente da caricare
        
    Returns:
        Account: L'oggetto Account se trovato, None altrimenti
    """
    return Account.query.get(int(user_id))

def init_auth(app):
    """
    Inizializza i sistemi di autenticazione.
    
    Configura sia Flask-Login per l'autenticazione basata su sessione
    che JWT per l'autenticazione basata su token.
    
    Args:
        app: L'istanza dell'applicazione Flask
    """
    # Inizializza Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Inizializza JWT
    jwt.init_app(app)
    
    # Configura la durata dei token JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

def create_user(username: str, email: str, password: str) -> Account:
    """
    Crea un nuovo utente nel sistema.
    
    Args:
        username: Username dell'utente
        email: Email dell'utente
        password: Password in chiaro dell'utente
        
    Returns:
        Account: L'oggetto Account creato
        
    Raises:
        ValidationError: Se la password non rispetta i criteri di sicurezza
    """
    # Valida la password
    is_valid, message = validate_password(password)
    if not is_valid:
        raise ValueError(message)
    
    # Crea il nuovo account
    account = Account(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )
    
    return account

def generate_auth_tokens(user_id: int) -> dict:
    """
    Genera access token e refresh token per l'utente.
    
    Args:
        user_id: ID dell'utente
        
    Returns:
        dict: Dizionario contenente access_token e refresh_token
    """
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }
