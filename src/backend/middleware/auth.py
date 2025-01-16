from functools import wraps
from flask import request, g, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from ..config.database import db
from ..models.models import Account
from ..middleware.response import APIResponse

def token_required(f):
    """Decorator per proteggere le route che richiedono autenticazione"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.info("Entrando nel decorator token_required")
        token = None

        # Cerca il token nell'header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return APIResponse.error(
                    message='Token mancante',
                    status_code=401,
                    error_code="UNAUTHORIZED"
                )

        if not token:
            return APIResponse.error(
                message='Token mancante',
                status_code=401,
                error_code="UNAUTHORIZED"
            )

        try:
            # Decodifica il token
            current_app.logger.info("Decodifica del token")
            payload = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            
            # Verifica se l'account esiste ed è attivo
            current_app.logger.info("Verifica account")
            db.session.rollback()  # Prova a pulire la sessione
            account = Account.query.get(payload['sub'])
            current_app.logger.info(f"Account trovato: {account is not None}, attivo: {account.is_active if account else None}")
            
            if not account:
                return APIResponse.error(
                    message='Account non trovato',
                    status_code=403,
                    error_code="FORBIDDEN"
                )
                
            if not account.is_active:
                current_app.logger.info("Account disattivato, ritorno 403")
                return APIResponse.error(
                    message='Account disattivato',
                    status_code=403,
                    error_code="FORBIDDEN"
                )
            
            # Memorizza l'ID dell'utente in g
            g.user_id = payload['sub']
            
        except jwt.ExpiredSignatureError:
            return APIResponse.error(
                message='Token scaduto',
                status_code=401,
                error_code="UNAUTHORIZED"
            )
        except jwt.InvalidTokenError:
            return APIResponse.error(
                message='Token non valido',
                status_code=401,
                error_code="UNAUTHORIZED"
            )
            
        return f(*args, **kwargs)

    return decorated


def generate_token(user_id):
    """Genera un JWT token per l'utente"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)


def validate_password(password):
    """Valida la password secondo criteri di sicurezza"""
    if len(password) < 8:
        return False, "La password deve essere di almeno 8 caratteri"
    
    if not any(char.isdigit() for char in password):
        return False, "La password deve contenere almeno un numero"
    
    if not any(char.isupper() for char in password):
        return False, "La password deve contenere almeno una lettera maiuscola"
    
    if not any(char.islower() for char in password):
        return False, "La password deve contenere almeno una lettera minuscola"
    
    return True, "Password valida"


def hash_password(password):
    """Genera l'hash della password"""
    return generate_password_hash(password)


def verify_password(hash_value, password):
    """Verifica la password con il suo hash"""
    return check_password_hash(hash_value, password)