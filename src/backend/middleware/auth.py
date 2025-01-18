"""
Middleware per l'autenticazione delle API.
Fornisce decoratori e funzioni per la gestione dei token JWT.
"""

from functools import wraps
from flask import request, g, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models import db
from ..models.models import Account
from ..middleware.response import APIResponse
from ..auth.password import hash_password, verify_password, validate_password

def token_required(f):
    """
    Decorator per proteggere le route che richiedono autenticazione.
    Verifica la presenza e validità del token JWT.
    """
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_app.logger.info("Entrando nel decorator token_required")
        
        # Get user identity from JWT
        user_id = get_jwt_identity()
        
        # Verifica se l'account esiste ed è attivo
        current_app.logger.info("Verifica account")
        account = Account.query.get(user_id)
        
        if not account:
            current_app.logger.warning(f"Account {user_id} non trovato")
            return APIResponse.error("Account non trovato", status_code=404)
            
        if not account.is_active:
            current_app.logger.warning(f"Account {user_id} non attivo")
            return APIResponse.error("Account non attivo", status_code=403)
        
        # Salva l'account nel contesto globale
        g.account = account
        current_app.logger.info(f"Account {user_id} autenticato con successo")
        
        return f(*args, **kwargs)
    
    return decorated

def generate_auth_tokens(user_id: int) -> dict:
    """
    Genera access token e refresh token per l'utente.
    
    Args:
        user_id: ID dell'utente
        
    Returns:
        dict: Dizionario contenente access_token e refresh_token
    """
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }