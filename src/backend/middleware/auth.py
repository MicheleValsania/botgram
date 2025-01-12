from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

def generate_token(user_id):
    """
    Genera un JWT token per l'utente
    """
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

def token_required(f):
    """
    Decorator per proteggere le route che richiedono autenticazione
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Cerca il token nell'header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token mancante'}), 401

        if not token:
            return jsonify({'message': 'Token mancante'}), 401

        try:
            # Decodifica il token
            payload = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            # Aggiunge l'ID dell'utente alla request
            request.user_id = payload['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token scaduto'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token non valido'}), 401

        return f(*args, **kwargs)

    return decorated

def validate_password(password):
    """
    Valida la password secondo criteri di sicurezza
    """
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
    """
    Genera l'hash della password
    """
    return generate_password_hash(password)

def verify_password(hash_value, password):
    """
    Verifica la password con il suo hash
    """
    return check_password_hash(hash_value, password)
