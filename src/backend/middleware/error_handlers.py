# src/backend/middleware/error_handlers.py

from flask import Blueprint, current_app, request
import json
from werkzeug.exceptions import HTTPException
from .response import APIResponse

error_handlers = Blueprint('error_handlers', __name__)

@error_handlers.app_errorhandler(json.JSONDecodeError)
def handle_json_error(e):
    """Gestisce JSON malformato"""
    current_app.logger.warning(f"JSON malformato: {str(e)}")
    return APIResponse.error(
        message="JSON non valido",
        status_code=400,
        error_code="INVALID_JSON",
        errors={"detail": str(e)}
    )

@error_handlers.app_errorhandler(400)
def handle_bad_request(e):
    """Gestisce richieste non valide"""
    return APIResponse.error(
        message="Richiesta non valida",
        status_code=400,
        error_code="BAD_REQUEST",
        errors=getattr(e, 'data', {})
    )

@error_handlers.app_errorhandler(401)
def handle_unauthorized(e):
    """Gestisce errori di autenticazione"""
    return APIResponse.error(
        message="Autenticazione richiesta",
        status_code=401,
        error_code="UNAUTHORIZED"
    )

@error_handlers.app_errorhandler(403)
def handle_forbidden(e):
    """Gestisce errori di autorizzazione"""
    return APIResponse.error(
        message="Accesso negato",
        status_code=403,
        error_code="FORBIDDEN"
    )

@error_handlers.app_errorhandler(404)
def handle_not_found(e):
    """Gestisce risorse non trovate"""
    return APIResponse.error(
        message="Risorsa non trovata",
        status_code=404,
        error_code="NOT_FOUND"
    )

@error_handlers.app_errorhandler(429)
def handle_rate_limit(e):
    """Gestisce superamento rate limit"""
    return APIResponse.error(
        message=str(e.description),
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    )

@error_handlers.app_errorhandler(Exception)
def handle_generic_error(e):
    """Gestisce tutti gli altri errori"""
    # Log dettagliato dell'errore
    current_app.logger.error(f"Errore non gestito: {str(e)}", exc_info=True)
    
    # In produzione, non esporre dettagli interni
    if current_app.config.get('ENV') == 'production':
        message = "Si è verificato un errore interno"
    else:
        message = str(e)
    
    return APIResponse.error(
        message=message,
        status_code=500,
        error_code="INTERNAL_ERROR"
    )

def init_error_handlers(app):
    """Inizializza gli error handler nell'app"""
    app.register_blueprint(error_handlers)