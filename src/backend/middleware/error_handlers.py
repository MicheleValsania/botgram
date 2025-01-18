"""
Gestori di errore centralizzati per l'applicazione.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError as MarshmallowValidationError
from ..middleware.response import APIResponse, ValidationError, AuthError, NotFoundError, APIError
import traceback

def register_error_handlers(app):
    """
    Registra i gestori di errore per l'applicazione.
    
    Args:
        app: L'istanza dell'applicazione Flask
    """
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        """Gestore per errori di autenticazione."""
        return APIResponse.error(
            message="Autenticazione richiesta",
            status_code=401,
            error_code="UNAUTHORIZED"
        )

    @app.errorhandler(403)
    def handle_forbidden(e):
        """Gestore per errori di autorizzazione."""
        return APIResponse.error(
            message="Accesso negato",
            status_code=403,
            error_code="FORBIDDEN"
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        """Gestore per risorse non trovate."""
        return APIResponse.error(
            message="Risorsa non trovata",
            status_code=404,
            error_code="NOT_FOUND"
        )

    @app.errorhandler(429)
    def handle_rate_limit(e):
        """Gestore per errori di rate limiting."""
        return APIResponse.error(
            message="Troppe richieste",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
        
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(e):
        """Gestore per errori di validazione di Marshmallow."""
        return APIResponse.error(
            message="Errore di validazione",
            status_code=400,
            error_code="VALIDATION_ERROR",
            errors=e.messages
        )
        
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Gestore per errori di validazione."""
        return APIResponse.error(
            message=e.message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            errors=e.errors if hasattr(e, 'errors') else None
        )
        
    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        """Gestore per errori di autenticazione."""
        return APIResponse.error(
            message=e.message,
            status_code=401,
            error_code="AUTH_ERROR"
        )
        
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        """Gestore per errori di risorsa non trovata."""
        return APIResponse.error(
            message=e.message,
            status_code=404,
            error_code="NOT_FOUND"
        )
        
    @app.errorhandler(APIError)
    def handle_api_error(e):
        """Gestore per errori API generici."""
        return APIResponse.error(
            message=e.message,
            status_code=e.status_code,
            error_code=e.error_code
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Gestore generico per tutte le altre eccezioni."""
        app.logger.error(f"Errore non gestito: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        if isinstance(e, HTTPException):
            return APIResponse.error(
                message=str(e),
                status_code=e.code,
                error_code="HTTP_ERROR"
            )
            
        return APIResponse.error(
            message="Errore interno del server",
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR"
        )