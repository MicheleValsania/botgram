from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .models import db
from .api import api
from .middleware.rate_limit import RateLimiter
from .middleware.logging import init_logging
from .middleware.response import APIResponse
from .auth.auth_manager import init_auth
from .config.config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_name: str = 'development') -> Flask:
    """Crea e configura l'applicazione Flask
    
    Args:
        config_name (str): Nome della configurazione da utilizzare ('development', 'testing', 'production')
        
    Returns:
        Flask: L'applicazione Flask configurata
    """
    # Carica le variabili d'ambiente
    load_dotenv()
    
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
    
    # Override configurazione da variabili d'ambiente
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config.get('SECRET_KEY', 'dev-key'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurazione JWT
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 ora
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 giorni
    
    # Inizializza le estensioni
    db.init_app(app)
    Migrate(app, db)
    
    # Inizializza i sistemi di autenticazione
    init_auth(app)
    
    # Configurazione rate limiter (prima degli error handler)
    app.config['RATELIMIT_ENABLED'] = True
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    
    # Inizializza il rate limiter
    RateLimiter.init_app(app)
    
    # Inizializza il logging
    init_logging(app)
    
    # Registra i blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    # Abilita CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Gestione errori globale
    @app.errorhandler(404)
    def not_found_error(error):
        return APIResponse.error(
            message="Risorsa non trovata",
            status_code=404
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return APIResponse.error(
            message="Errore interno del server",
            status_code=500
        )
        
    @app.errorhandler(403)
    def forbidden_error(error):
        return APIResponse.error(
            message="Accesso negato",
            status_code=403
        )

    # Route di healthcheck
    @app.route('/health')
    def health_check():
        return APIResponse.success(
            data={
                "status": "healthy",
                "version": os.getenv('APP_VERSION', '1.0.0'),
                "environment": app.config.get('ENV', 'development')
            }
        )

    # Configura headers di sicurezza
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()