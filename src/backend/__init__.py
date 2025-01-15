from flask import Flask
from flask_migrate import Migrate
from .config.database import db
from .middleware.rate_limit import RateLimiter
from .middleware.logging import init_logging
from .config.config import DevelopmentConfig, TestingConfig, ProductionConfig
from .middleware.response import APIResponse
from .middleware.error_handlers import init_error_handlers

def create_app(config_name='development'):
    """Create and configure the Flask application."""
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
    
    # Configurazione del rate limiter
    app.config['RATELIMIT_ENABLED'] = True
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    

    # Inizializza gli error handler
    init_error_handlers(app)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    RateLimiter.init_app(app)
    
    # Inizializza il logging
    init_logging(app)
    
    # Importa e registra i blueprint qui, dopo l'inizializzazione delle estensioni
    from .api import api
    app.register_blueprint(api, url_prefix='/api')
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"[DEBUG] Unhandled exception: {str(e)}")
        app.logger.error(f"[DEBUG] Exception type: {type(e)}")
        return APIResponse.error(
            message="Internal server error",
            status_code=500
        ), 500
    
    return app