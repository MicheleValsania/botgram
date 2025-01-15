from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import HTTPException, BadRequest, NotFound, Unauthorized, Forbidden
from marshmallow import ValidationError
import json
from .response import APIResponse

def init_error_handlers(app):
    @app.errorhandler(json.JSONDecodeError)
    @app.errorhandler(BadRequest)  # Copre anche errori di JSON malformato
    def handle_bad_request(e):
        if isinstance(e, json.JSONDecodeError):
            error_code = 'INVALID_JSON'
            message = 'JSON non valido'
        else:
            error_code = 'BAD_REQUEST'
            message = str(e)
            
        return APIResponse.error(
            message=message,
            status_code=400,
            error_code=error_code
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
        
        # Messaggio generico in produzione
        if app.config.get('ENV') == 'production':
            message = "Errore interno del server"
        else:
            message = str(e)
        
        return APIResponse.error(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )

    # Handler specifico per il parsing JSON
    @app.before_request
    def handle_json():
        if request.is_json:
            try:
                request.get_json()
            except json.JSONDecodeError:
                return APIResponse.error(
                    message="JSON non valido",
                    status_code=400,
                    error_code="INVALID_JSON"
                )