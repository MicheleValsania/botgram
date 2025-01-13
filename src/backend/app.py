from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .config.database import db
from .api import api
from .middleware.rate_limit import RateLimiter
from .middleware.logging import init_logging
from .middleware.response import APIResponse

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
    
    # Configurazione CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Carica la configurazione appropriata
    if config_name == 'testing':
        app.config.from_object('backend.config.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('backend.config.ProductionConfig')
    else:
        app.config.from_object('backend.config.DevelopmentConfig')
    
    # Override configurazione da variabili d'ambiente
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config.get('SECRET_KEY', 'dev-key'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', app.config.get('SQLALCHEMY_DATABASE_URI'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inizializza le estensioni
    db.init_app(app)
    Migrate(app, db)
    
    # Inizializza il rate limiter
    RateLimiter.init_app(app)
    
    # Inizializza il logging
    init_logging(app)
    
    # Registra i blueprint
    app.register_blueprint(api, url_prefix='/api')
    
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