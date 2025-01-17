from flask import Flask, jsonify, request
from flask_migrate import Migrate
from .models import db
from .middleware.rate_limit import RateLimiter
from .middleware.logging import init_logging
from .config.config import DevelopmentConfig, TestingConfig, ProductionConfig
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, BadRequest
from .middleware.response import APIResponse
import json

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
    
    # Inizializza le estensioni
    db.init_app(app)
    Migrate(app, db)
    
    # Inizializza il logging
    init_logging(app)
    
    # Configurazione rate limiter (prima degli error handler)
    app.config['RATELIMIT_ENABLED'] = True
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    
    # Inizializza il rate limiter
    RateLimiter.init_app(app)
    
    # Gestione JSON malformato
    @app.before_request
    def handle_json():
        if request.is_json:
            try:
                request.get_json()
            except json.JSONDecodeError as e:
                return APIResponse.error(
                    message="JSON non valido",
                    status_code=400,
                    error_code="INVALID_JSON"
                )
    
    # Registra gli error handler
    @app.errorhandler(json.JSONDecodeError)
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        if isinstance(e, json.JSONDecodeError):
            return APIResponse.error(
                message="JSON non valido",
                status_code=400,
                error_code="INVALID_JSON"
            )
        return APIResponse.error(
            message=str(e),
            status_code=400,
            error_code="BAD_REQUEST"
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return APIResponse.error(
            message="Errore di validazione",
            status_code=400,
            error_code="VALIDATION_ERROR",
            errors=e.messages
        )

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return APIResponse.error(
            message="Autenticazione richiesta",
            status_code=401,
            error_code="UNAUTHORIZED"
        )

    @app.errorhandler(403)
    def handle_forbidden(e):
        return APIResponse.error(
            message="Accesso negato",
            status_code=403,
            error_code="FORBIDDEN"
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        return APIResponse.error(
            message="Risorsa non trovata",
            status_code=404,
            error_code="NOT_FOUND"
        )

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        app.logger.error(f"Errore non gestito: {str(e)}", exc_info=True)
        message = "Errore interno" if app.config['ENV'] == 'production' else str(e)
        return APIResponse.error(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
    
    # Registra i blueprint
    from .api import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app