"""
Endpoints per l'autenticazione.
"""

from datetime import datetime, timezone
from flask import request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    get_jwt, jwt_required
)
from marshmallow import ValidationError as MarshmallowValidationError
from ...models import db
from ...models.models import Account
from ...auth.password import verify_password
from ...auth.security import (
    check_brute_force_protection, record_failed_login,
    reset_failed_login_attempts, blacklist_token,
    require_not_blacklisted, log_security_event
)
from ...auth.auth_manager import generate_auth_tokens
from ...auth.password import hash_password, validate_password
from ...schemas.schemas import AccountSchema, LoginSchema, LoginResponseSchema
from ...middleware.response import APIResponse, handle_api_errors, ValidationError, AuthError, NotFoundError
from ...middleware.rate_limit import auth_rate_limits, api_rate_limits
from ...middleware.logging import log_request
from flask import Blueprint

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
        created_at=datetime.now(timezone.utc)
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
        error_messages = [f"{field}: {msg}" for field, messages in e.messages.items() 
                        for msg in (messages if isinstance(messages, list) else [messages])]
        raise ValidationError(
            message=", ".join(error_messages),
            errors=e.messages
        )
    
    account = Account.query.filter_by(email=data['email']).first()
    
    if not account:
        log_security_event('login_failed', 
                         details={'email': data['email'], 'reason': 'account_not_found'},
                         request=request)
        return APIResponse.error(message="Invalid email or password", status_code=401)
    
    # Check brute force protection
    allowed, error_message = check_brute_force_protection(account)
    if not allowed:
        log_security_event('login_blocked',
                         account_id=account.id,
                         details={'reason': 'brute_force_protection'},
                         request=request)
        return APIResponse.error(message=error_message, status_code=429)
    
    if not verify_password(data['password'], account.password_hash):
        record_failed_login(account)
        log_security_event('login_failed',
                         account_id=account.id,
                         details={'reason': 'invalid_password'},
                         request=request)
        return APIResponse.error(message="Invalid email or password", status_code=401)
    
    # Reset failed login attempts on successful login
    reset_failed_login_attempts(account)
    
    # Update last login timestamp
    account.last_login = datetime.now(timezone.utc)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=account.id)
    refresh_token = create_refresh_token(identity=account.id)
    
    log_security_event('login_success',
                     account_id=account.id,
                     request=request)
    
    return APIResponse.success(data={
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': account.id,
            'email': account.email,
            'username': account.username
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@require_not_blacklisted()
@handle_api_errors
def logout():
    """Endpoint per il logout."""
    jwt = get_jwt()
    user_id = get_jwt_identity()
    
    blacklist_token(
        token_jti=jwt['jti'],
        token_type='access',
        user_id=user_id,
        expires=datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    )
    
    log_security_event('logout',
                     account_id=user_id,
                     request=request,
                     details={'token_jti': jwt['jti']})
    
    return APIResponse.success(message='Logout successful')

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@require_not_blacklisted()
@handle_api_errors
def get_me():
    """Endpoint per ottenere i dati dell'utente corrente."""
    user_id = get_jwt_identity()
    user = Account.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    return APIResponse.success(
        data=account_schema.dump(user),
        message='Dati utente recuperati con successo'
    )

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
@require_not_blacklisted()
@handle_api_errors
def update_me():
    """Endpoint per aggiornare i dati dell'utente corrente."""
    user_id = get_jwt_identity()
    user = Account.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
        
    try:
        data = account_schema.load(request.get_json(), partial=True)
    except MarshmallowValidationError as e:
        error_messages = [f"{field}: {msg}" for field, messages in e.messages.items() 
                        for msg in (messages if isinstance(messages, list) else [messages])]
        raise ValidationError(
            message=", ".join(error_messages),
            errors=e.messages
        )
    
    # Update allowed fields
    allowed_fields = ['username', 'email']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # Handle password update separately
    if 'password' in data:
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            raise ValidationError(message=message)
        user.password_hash = hash_password(data['password'])
    
    db.session.commit()
    
    return APIResponse.success(
        data=account_schema.dump(user),
        message='Account updated successfully'
    )

@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
@require_not_blacklisted()
@handle_api_errors
def delete_me():
    """Endpoint per disattivare l'account corrente."""
    user_id = get_jwt_identity()
    user = Account.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    user.is_active = False
    db.session.commit()
    
    return APIResponse.success(message='Account successfully deactivated')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@require_not_blacklisted()
@handle_api_errors
def refresh():
    """Endpoint per il refresh del token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return APIResponse.success(data={
        'access_token': access_token
    })