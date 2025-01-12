from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from ..models.models import Account, db
from ..middleware.auth import generate_token, token_required, hash_password, verify_password, validate_password
from ..schemas.schemas import AccountSchema, LoginSchema, LoginResponseSchema

auth_bp = Blueprint('auth', __name__)
account_schema = AccountSchema()
login_schema = LoginSchema()
login_response_schema = LoginResponseSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Valida i dati in ingresso
        data = account_schema.load(request.get_json())
        
        # Valida la password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Verifica se l'username esiste già
        if Account.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username già in uso'}), 400
            
        # Verifica se l'email esiste già
        if Account.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email già registrata'}), 400
        
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
        
        return jsonify(login_response_schema.dump(response_data)), 201
        
    except ValidationError as e:
        return jsonify({'message': 'Dati non validi', 'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Errore durante la registrazione', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Valida i dati in ingresso
        data = login_schema.load(request.get_json())
        
        # Cerca l'account
        account = Account.query.filter_by(username=data['username']).first()
        
        # Verifica le credenziali
        if not account or not verify_password(account.password_hash, data['password']):
            return jsonify({'message': 'Credenziali non valide'}), 401
            
        if not account.is_active:
            return jsonify({'message': 'Account disattivato'}), 403
        
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
        
        return jsonify(login_response_schema.dump(response_data)), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Dati non validi', 'errors': e.messages}), 400
    except Exception as e:
        return jsonify({'message': 'Errore durante il login', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me():
    try:
        # Ottiene l'account dell'utente autenticato
        account = Account.query.get(request.user_id)
        if not account:
            return jsonify({'message': 'Account non trovato'}), 404
            
        return jsonify(account_schema.dump(account)), 200
        
    except Exception as e:
        return jsonify({'message': 'Errore durante il recupero dei dati', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_me():
    try:
        # Ottiene l'account dell'utente autenticato
        account = Account.query.get(request.user_id)
        if not account:
            return jsonify({'message': 'Account non trovato'}), 404
        
        # Valida i dati in ingresso
        data = request.get_json()
        
        # Aggiorna solo i campi forniti
        if 'email' in data:
            # Verifica se l'email esiste già per un altro account
            existing_account = Account.query.filter_by(email=data['email']).first()
            if existing_account and existing_account.id != account.id:
                return jsonify({'message': 'Email già registrata'}), 400
            account.email = data['email']
            
        if 'password' in data:
            # Valida la nuova password
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'message': message}), 400
            account.password_hash = hash_password(data['password'])
        
        db.session.commit()
        
        return jsonify(account_schema.dump(account)), 200
        
    except ValidationError as e:
        return jsonify({'message': 'Dati non validi', 'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Errore durante l\'aggiornamento', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['DELETE'])
@token_required
def delete_me():
    try:
        # Ottiene l'account dell'utente autenticato
        account = Account.query.get(request.user_id)
        if not account:
            return jsonify({'message': 'Account non trovato'}), 404
        
        # Disattiva l'account invece di eliminarlo
        account.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Account disattivato con successo'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Errore durante la disattivazione', 'error': str(e)}), 500