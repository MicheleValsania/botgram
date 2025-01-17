from flask import Blueprint, request, g, current_app
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
import json
from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError
from ...models.models import Account, db
from ...middleware.auth import token_required, generate_auth_tokens, hash_password, verify_password, validate_password
from ...schemas.schemas import AccountSchema, LoginSchema, LoginResponseSchema
from ...middleware.response import APIResponse, handle_api_errors
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
    """Endpoint per la registrazione di un nuovo account"""
    try:
        data = account_schema.load(request.get_json())
    except Exception as e:
        return APIResponse.error(message='Dati non validi', errors=str(e), status_code=400)
    
    # Valida la password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return APIResponse.error(message=message, status_code=400)
    
    # Verifica username e email duplicati
    if Account.query.filter_by(username=data['username']).first():
        return APIResponse.error(message='Username già in uso', status_code=400)
        
    if Account.query.filter_by(email=data['email']).first():
        return APIResponse.error(message='Email già registrata', status_code=400)
    
    # Crea il nuovo account
    hashed_password = hash_password(data['password'])
    current_app.logger.info(f"Password fornita durante registrazione: {data['password']}")
    current_app.logger.info(f"Password hash durante registrazione: {hashed_password}")
    
    new_account = Account(
        username=data['username'],
        password_hash=hashed_password,
        email=data['email'],
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    # Salva nel database
    db.session.add(new_account)
    db.session.commit()
    
    # Login automatico dopo la registrazione
    login_user(new_account)
    
    # Genera i token
    tokens = generate_auth_tokens(new_account.id)
    
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
@log_request()
def login():
    try:
        json_data = request.get_json()
        current_app.logger.info(f"Raw request data: {json_data}")
    except (json.JSONDecodeError, BadRequest):
        return APIResponse.error(
            message="JSON non valido",
            status_code=400,
            error_code="INVALID_JSON"
        )
        
    try:
        data = login_schema.load(json_data)
        current_app.logger.info(f"Validated data: {data}")
    except ValidationError as e:
        return APIResponse.error(
            message="Errore di validazione",
            status_code=400,
            error_code="VALIDATION_ERROR",
            errors=e.messages
        )
    
    # Trova l'account
    account = Account.query.filter_by(username=data['username']).first()
    if not account:
        return APIResponse.error(
            message="Username non trovato",
            status_code=401,
            error_code="INVALID_USERNAME"
        )
    
    current_app.logger.info(f"Password hash: {account.password_hash}")
    current_app.logger.info(f"Password fornita: {data['password']}")
    
    if not verify_password(data['password'], account.password_hash):
        return APIResponse.error(
            message="Password non valida",
            status_code=401,
            error_code="INVALID_PASSWORD"
        )
    
    if not account.is_active:
        return APIResponse.error(
            message="Account disattivato",
            status_code=403,
            error_code="ACCOUNT_DISABLED"
        )
    
    # Aggiorna last_login
    account.last_login = datetime.utcnow()
    db.session.commit()
    
    # Login con Flask-Login
    login_user(account)
    
    # Genera i token
    tokens = generate_auth_tokens(account.id)
    
    response_data = {
        'user': account_schema.dump(account),
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_type': tokens['token_type']
    }
    
    return APIResponse.success(
        data=response_data,
        message='Login effettuato con successo',
        status_code=200
    )

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Endpoint per il logout"""
    logout_user()
    return APIResponse.success(message='Logout effettuato con successo')

@auth_bp.route('/me', methods=['GET'])
@token_required
@api_rate_limits()
@handle_api_errors
@log_request()
def get_me():
    """Endpoint per ottenere i dati dell'utente corrente"""
    account = Account.query.get(g.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
        
    return APIResponse.success(
        data=account_schema.dump(account),
        message='Dati utente recuperati con successo'
    )

@auth_bp.route('/me', methods=['PUT'])
@token_required
@handle_api_errors
@log_request()
def update_me():
    """Endpoint per aggiornare i dati dell'utente corrente"""
    account = Account.query.get(g.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
    
    try:
        data = account_schema.load(request.get_json(), partial=True)
    except ValidationError as e:
        return APIResponse.error(
            message="Errore di validazione",
            status_code=400,
            error_code="VALIDATION_ERROR",
            errors=e.messages
        )
    
    # Aggiorna i campi modificabili
    for field in ['email', 'username']:
        if field in data:
            setattr(account, field, data[field])
    
    # Se è presente una nuova password, validala e aggiornala
    if 'password' in data:
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return APIResponse.error(message=message, status_code=400)
        account.password_hash = hash_password(data['password'])
    
    db.session.commit()
    
    return APIResponse.success(
        data=account_schema.dump(account),
        message='Account aggiornato con successo'
    )

@auth_bp.route('/me', methods=['DELETE'])
@token_required
@handle_api_errors
@log_request()
def delete_me():
    """Endpoint per disattivare l'account corrente"""
    account = Account.query.get(g.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
    
    account.is_active = False
    db.session.commit()
    
    # Logout dopo la disattivazione
    logout_user()
    
    return APIResponse.success(message='Account disattivato con successo')