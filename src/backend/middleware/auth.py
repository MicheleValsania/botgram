from functools import wraps
from flask import request, g, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db
from ..models.models import Account
from ..middleware.response import APIResponse

def token_required(f):
    """Decorator per proteggere le route che richiedono autenticazione"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_app.logger.info("Entrando nel decorator token_required")
        
        # Get user identity from JWT
        user_id = get_jwt_identity()
        
        # Verifica se l'account esiste ed è attivo
        current_app.logger.info("Verifica account")
        db.session.rollback()  # Prova a pulire la sessione
        account = Account.query.get(user_id)
        current_app.logger.info(f"Account trovato: {account is not None}, attivo: {account.is_active if account else None}")
        
        if not account:
            return APIResponse.error(
                message='Account non trovato',
                status_code=401,
                error_code="UNAUTHORIZED"
            )
            
        if not account.is_active:
            return APIResponse.error(
                message='Account disattivato',
                status_code=403,
                error_code="FORBIDDEN"
            )

        # Salva l'ID dell'utente nel contesto globale
        g.user_id = user_id
        
        return f(*args, **kwargs)
    
    return decorated

def generate_auth_tokens(user_id):
    """Genera access token e refresh token per l'utente"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

def validate_password(password):
    """Valida la password secondo criteri di sicurezza"""
    if len(password) < 8:
        return False, "La password deve essere lunga almeno 8 caratteri"
    
    if not any(c.isupper() for c in password):
        return False, "La password deve contenere almeno una lettera maiuscola"
        
    if not any(c.islower() for c in password):
        return False, "La password deve contenere almeno una lettera minuscola"
        
    if not any(c.isdigit() for c in password):
        return False, "La password deve contenere almeno un numero"
        
    return True, "Password valida"

def hash_password(password):
    """Genera l'hash della password"""
    current_app.logger.info(f"Generazione hash per password: {password}")
    hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    current_app.logger.info(f"Hash generato: {hashed}")
    return hashed

def verify_password(password, hash_value):
    """Verifica la password con il suo hash"""
    try:
        current_app.logger.info(f"Verifica password - Hash: {hash_value}, Password: {password}")
        result = check_password_hash(hash_value, password)
        current_app.logger.info(f"Risultato verifica: {result}")
        return result
    except Exception as e:
        current_app.logger.error(f"Errore durante la verifica della password: {str(e)}")
        return False