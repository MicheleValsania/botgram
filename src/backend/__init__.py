"""
Inizializzazione dell'applicazione Flask.
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config.config import config
from .models import db
from .auth.auth_manager import init_auth
from .middleware.error_handlers import register_error_handlers
from .middleware.rate_limit import RateLimiter
from .api import register_blueprints

def create_app(config_name='development'):
    """
    Factory per la creazione dell'applicazione Flask.
    
    Args:
        config_name: Nome della configurazione da utilizzare
        
    Returns:
        Flask: L'applicazione Flask configurata
    """
    app = Flask(__name__)
    
    # Carica la configurazione
    app.config.from_object(config[config_name])
    
    # Inizializza le estensioni
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    RateLimiter.init_app(app)
    
    with app.app_context():
        # Inizializza l'autenticazione
        init_auth(app)
        
        # Registra i gestori di errore
        register_error_handlers(app)
        
        # Registra i blueprint
        register_blueprints(app)
        
        # Crea le tabelle del database
        db.create_all()
    
    return app