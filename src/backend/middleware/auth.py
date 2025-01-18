"""
Middleware per l'autenticazione delle API.
Fornisce decoratori per la protezione delle route.
"""

from functools import wraps
from flask import request, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from ..models import db
from ..models.models import Account
from ..middleware.response import APIResponse, AuthError, NotFoundError
from ..auth.auth_manager import generate_auth_tokens

def token_required(f):
    """
    Decorator per proteggere le route che richiedono autenticazione.
    Verifica la presenza e validità del token JWT.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.info("Entrando nel decorator token_required")
        
        try:
            # Verifica il token JWT
            verify_jwt_in_request()
            
            # Get user identity from JWT
            user_id = get_jwt_identity()
            
            # Verifica se l'account esiste ed è attivo
            current_app.logger.info("Verifica account")
            account = Account.query.get(user_id)
            
            if not account:
                current_app.logger.warning(f"Account {user_id} non trovato")
                raise NotFoundError("Account non trovato")
                
            if not account.is_active:
                current_app.logger.warning(f"Account {user_id} non attivo")
                raise AuthError("Account non attivo")
            
            # Salva l'account nel contesto globale
            g.current_user = account
            current_app.logger.info(f"Account {user_id} autenticato con successo")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Errore di autenticazione: {str(e)}")
            if isinstance(e, (NotFoundError, AuthError)):
                raise
            raise AuthError("Token non valido")
    
    return decorated