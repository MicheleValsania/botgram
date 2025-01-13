"""
Backend module initialization
"""
from flask import Flask
from flask_migrate import Migrate
from .config.database import db
from .api import api
from .middleware.rate_limit import RateLimiter
from .middleware.logging import init_logging
# Importazione diretta dalle classi di configurazione
from .config.config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_name='development'):
    """Create and configure the Flask application.
    
    Args:
        config_name (str): The name of the configuration to use 
                          ('development', 'testing', or 'production')
    
    Returns:
        Flask: The configured Flask application instance
    """
    app = Flask(__name__)
    
    # Map delle configurazioni
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    # Carica la configurazione appropriata
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    
    # Inizializza il rate limiter solo se non siamo in testing
    if not app.config['TESTING']:
        RateLimiter.init_app(app)
    
    # Inizializza il logging
    init_logging(app)
    
    # Registra i blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    return app