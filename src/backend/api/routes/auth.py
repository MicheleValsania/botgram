"""
Endpoints per l'autenticazione.
"""

from flask import Blueprint, request, g, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import json
from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError as MarshmallowValidationError
from ...models.models import Account, db
from ...middleware.auth import token_required
from ...auth.auth_manager import generate_auth_tokens
from ...auth.password import hash_password, verify_password, validate_password
from ...schemas.schemas import AccountSchema, LoginSchema, LoginResponseSchema
from ...middleware.response import APIResponse, handle_api_errors, ValidationError, AuthError, NotFoundError
from ...middleware.rate_limit import auth_rate_limits, api_rate_limits
from ...middleware.logging import log_request

auth_bp = Blueprint('auth', __name__)
account_schema = AccountSchema()
login_schema = LoginSchema()
login_response_schema = LoginResponseSchema()

@auth_bp.route('/register', methods=['POST'])
@auth_rate_limits() 
@handle_api_errors
def register():
    """Endpoint per la registrazione di un nuovo account."""
    try:
        data = account_schema.load(request.get_json())
    except MarshmallowValidationError as e:
        # Costruisci un messaggio di errore più descrittivo
        error_messages = []
        for field, messages in e.messages.items():
            if isinstance(messages, list):
                error_messages.extend([f"{field}: {msg}" for msg in messages])
            else:
                error_messages.append(f"{field}: {messages}")
        
        raise ValidationError(
            message=", ".join(error_messages),
            errors=e.messages
        )
    
    # Valida la password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        raise ValidationError(message=message)
    
    # Verifica username e email duplicati
    if Account.query.filter_by(username=data['username']).first():
        raise ValidationError(message='Username già in uso')
        
    if Account.query.filter_by(email=data['email']).first():
        raise ValidationError(message='Email già registrata')
    
    # Crea il nuovo account
    hashed_password = hash_password(data['password'])
    
    new_account = Account(
        username=data['username'],
        password_hash=hashed_password,
        email=data['email'],
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.session.add(new_account)
    db.session.commit()
    
    # Genera i token
    tokens = generate_auth_tokens(new_account.id)
    
    # Prepara la risposta
    response_data = {
        'user': account_schema.dump(new_account),
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_type': tokens['token_type']
    }
    
    return APIResponse.success(
        data=response_data,
        message='Account creato con successo',
        status_code=201
    )

@auth_bp.route('/login', methods=['POST'])
@auth_rate_limits()
@handle_api_errors
def login():
    """Endpoint per il login."""
    try:
        data = login_schema.load(request.get_json())
    except MarshmallowValidationError as e:
        # Costruisci un messaggio di errore più descrittivo
        error_messages = []
        for field, messages in e.messages.items():
            if isinstance(messages, list):
                error_messages.extend([f"{field}: {msg}" for msg in messages])
            else:
                error_messages.append(f"{field}: {messages}")
        
        raise ValidationError(
            message=", ".join(error_messages),
            errors=e.messages
        )
    
    # Cerca l'account
    account = Account.query.filter_by(email=data['email']).first()
    
    if not account:
        raise NotFoundError(message='Account non trovato')
        
    if not account.is_active:
        raise AuthError(message='Account non attivo')
    
    # Verifica la password
    if not verify_password(data['password'], account.password_hash):
        raise AuthError(message='Password non valida')
    
    # Aggiorna last_login
    account.last_login = datetime.utcnow()
    db.session.commit()
    
    # Genera i token
    tokens = generate_auth_tokens(account.id)
    
    # Prepara la risposta
    response_data = {
        'user': account_schema.dump(account),
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_type': tokens['token_type']
    }
    
    return APIResponse.success(
        data=response_data,
        message='Login effettuato con successo'
    )

@auth_bp.route('/logout', methods=['POST'])
@token_required
@handle_api_errors
def logout():
    """Endpoint per il logout."""
    # Qui potremmo aggiungere il token alla blacklist
    return APIResponse.success(message='Logout effettuato con successo')

@auth_bp.route('/me', methods=['GET'])
@token_required
@handle_api_errors
def get_me():
    """Endpoint per ottenere i dati dell'utente corrente."""
    return APIResponse.success(
        data=account_schema.dump(g.current_user),
        message='Dati utente recuperati con successo'
    )

@auth_bp.route('/me', methods=['PUT'])
@token_required
@handle_api_errors
def update_me():
    """Endpoint per aggiornare i dati dell'utente corrente."""
    try:
        data = account_schema.load(request.get_json(), partial=True)
    except MarshmallowValidationError as e:
        # Costruisci un messaggio di errore più descrittivo
        error_messages = []
        for field, messages in e.messages.items():
            if isinstance(messages, list):
                error_messages.extend([f"{field}: {msg}" for msg in messages])
            else:
                error_messages.append(f"{field}: {messages}")
        
        raise ValidationError(
            message=", ".join(error_messages),
            errors=e.messages
        )
    
    # Verifica username e email duplicati se presenti
    if 'username' in data:
        existing = Account.query.filter_by(username=data['username']).first()
        if existing and existing.id != g.current_user.id:
            raise ValidationError(message='Username già in uso')
            
    if 'email' in data:
        existing = Account.query.filter_by(email=data['email']).first()
        if existing and existing.id != g.current_user.id:
            raise ValidationError(message='Email già registrata')
    
    # Aggiorna la password se presente
    if 'password' in data:
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            raise ValidationError(message=message)
        g.current_user.password_hash = hash_password(data['password'])
        
    # Aggiorna gli altri campi
    for key, value in data.items():
        if key != 'password' and hasattr(g.current_user, key):
            setattr(g.current_user, key, value)
    
    db.session.commit()
    
    return APIResponse.success(
        data=account_schema.dump(g.current_user),
        message='Account aggiornato con successo'
    )

@auth_bp.route('/me', methods=['DELETE'])
@token_required
@handle_api_errors
def delete_me():
    """Endpoint per disattivare l'account corrente."""
    g.current_user.is_active = False
    db.session.commit()
    
    return APIResponse.success(message='Account disattivato con successo')

@auth_bp.route('/refresh', methods=['POST'])
@token_required
@handle_api_errors
def refresh():
    """Endpoint per il refresh del token."""
    current_user_id = get_jwt_identity()
    
    # Genera nuovi token
    tokens = generate_auth_tokens(current_user_id)
    
    return APIResponse.success(
        data=tokens,
        message='Token aggiornato con successo'
    )