from functools import wraps
from flask import jsonify, current_app
from typing import Any, Dict, Optional, Union
import traceback

class APIResponse:
    """Classe per standardizzare le risposte API"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict] = None
    ) -> tuple:
        """
        Crea una risposta di successo standardizzata
        
        Args:
            data: Dati da restituire
            message: Messaggio di successo
            status_code: Codice HTTP
            meta: Metadati aggiuntivi (paginazione, ecc.)
        """
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response["meta"] = meta
            
        return jsonify(response), status_code

    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: Optional[str] = None,
        errors: Optional[Dict] = None
    ) -> tuple:
        """
        Crea una risposta di errore standardizzata
        
        Args:
            message: Messaggio di errore
            status_code: Codice HTTP
            error_code: Codice errore interno
            errors: Dettagli errori di validazione
        """
        response = {
            "success": False,
            "message": message
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if errors:
            response["errors"] = errors
            
        return jsonify(response), status_code

def handle_api_errors(f):
    """Decorator per gestire gli errori delle API in modo uniforme"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return APIResponse.error(
                message="Validation error",
                status_code=400,
                errors=e.messages
            )
        except AuthError as e:
            return APIResponse.error(
                message=str(e),
                status_code=401,
                error_code="AUTH_ERROR"
            )
        except NotFoundError as e:
            return APIResponse.error(
                message=str(e),
                status_code=404,
                error_code="NOT_FOUND"
            )
        except Exception as e:
            # Log dell'errore dettagliato in ambiente di sviluppo
            if current_app.debug:
                print(traceback.format_exc())
            
            return APIResponse.error(
                message="Internal server error",
                status_code=500,
                error_code="INTERNAL_ERROR"
            )
    return wrapped

# Custom Exceptions
class APIError(Exception):
    """Classe base per errori API custom"""
    def __init__(self, message: str, status_code: int = 400, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ValidationError(APIError):
    """Errore di validazione dati"""
    def __init__(self, message: str = "Validation error", errors: Optional[Dict] = None):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")
        self.errors = errors

class AuthError(APIError):
    """Errore di autenticazione"""
    def __init__(self, message: str = "Authentication error"):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR")

class NotFoundError(APIError):
    """Errore risorsa non trovata"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")