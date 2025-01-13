from flask import Blueprint, request
from datetime import datetime
from ...models.models import Account, db
from ...middleware.auth import generate_token, token_required, hash_password, verify_password, validate_password
from ...schemas.schemas import AccountSchema, LoginSchema, LoginResponseSchema
from ...middleware.response import APIResponse, handle_api_errors
from ...middleware.rate_limit import auth_rate_limits
from ...middleware.logging import log_request

auth_bp = Blueprint('auth', __name__)
account_schema = AccountSchema()
login_schema = LoginSchema()
login_response_schema = LoginResponseSchema()

@auth_bp.route('/register', methods=['POST'])
@auth_rate_limits()     
@handle_api_errors      
@log_request()  
def register():
    """Endpoint per la registrazione di un nuovo account"""
    # Valida i dati in ingresso
    
    data = request.get_json()
    
    if Account.query.filter_by(username=data['username']).first():
        return APIResponse.error(message='Username già in uso', status_code=400)
        
    # Poi controlla se l'email esiste già
    if Account.query.filter_by(email=data['email']).first():
        return APIResponse.error(message='Email già registrata', status_code=400)
    
    
    # Valida la password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return APIResponse.error(message=message, status_code=400)
    
    data = account_schema.load(request.get_json())

    # Verifica se l'username esiste già
    if Account.query.filter_by(username=data['username']).first():
        return APIResponse.error(message='Username già in uso', status_code=400)
        
    # Verifica se l'email esiste già
    if Account.query.filter_by(email=data['email']).first():
        return APIResponse.error(message='Email già registrata', status_code=400)
    
    # Crea il nuovo account
    new_account = Account(
        username=data['username'],
        password_hash=hash_password(data['password']),
        email=data['email'],
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    # Salva nel database
    db.session.add(new_account)
    db.session.commit()
    
    # Genera il token
    token = generate_token(new_account.id)
    
    # Prepara la risposta
    response_data = {
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 24 * 60 * 60,  # 24 ore in secondi
        'user_id': new_account.id
    }
    
    return APIResponse.success(
        data=login_response_schema.dump(response_data),
        message='Registrazione completata con successo',
        status_code=201
    )

@auth_bp.route('/login', methods=['POST'])
@auth_rate_limits()     
@handle_api_errors      
@log_request() 
def login():
    """Endpoint per il login"""
    # Valida i dati in ingresso
    data = login_schema.load(request.get_json())
    
    # Cerca l'account
    account = Account.query.filter_by(username=data['username']).first()
    
    # Verifica le credenziali
    if not account or not verify_password(account.password_hash, data['password']):
        return APIResponse.error(message='Credenziali non valide', status_code=401)
        
    if not account.is_active:
        return APIResponse.error(message='Account disattivato', status_code=403)
    
    # Aggiorna last_login
    account.last_login = datetime.utcnow()
    db.session.commit()
    
    # Genera il token
    token = generate_token(account.id)
    
    # Prepara la risposta
    response_data = {
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 24 * 60 * 60,  # 24 ore in secondi
        'user_id': account.id
    }
    
    return APIResponse.success(
        data=login_response_schema.dump(response_data),
        message='Login effettuato con successo'
    )

@auth_bp.route('/me', methods=['GET'])
@auth_rate_limits()     
@handle_api_errors      
@log_request() 
def get_me():
    """Endpoint per ottenere i dati dell'utente corrente"""
    # Ottiene l'account dell'utente autenticato
    account = Account.query.get(request.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
        
    return APIResponse.success(
        data=account_schema.dump(account),
        message='Dati utente recuperati con successo'
    )

@auth_bp.route('/me', methods=['PUT'])
@auth_rate_limits()     
@handle_api_errors      
@log_request() 
def update_me():
    """Endpoint per aggiornare i dati dell'utente corrente"""
    account = Account.query.get(request.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
    
    data = request.get_json()
    
    if 'email' in data:
        existing_account = Account.query.filter_by(email=data['email']).first()
        if existing_account and existing_account.id != account.id:
            return APIResponse.error(message='Email già registrata', status_code=400)
        account.email = data['email']
        
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
@auth_rate_limits()     
@handle_api_errors      
@log_request() 
def delete_me():
    """Endpoint per disattivare l'account corrente"""
    account = Account.query.get(request.user_id)
    if not account:
        return APIResponse.error(message='Account non trovato', status_code=404)
    
    account.is_active = False
    db.session.commit()
    
    return APIResponse.success(message='Account disattivato con successo')