from flask import Blueprint, request
from marshmallow import ValidationError
from ..models.models import Configuration, db
from ..middleware.auth import token_required
from ..schemas.schemas import ConfigurationSchema
from ..middleware.response import APIResponse, handle_api_errors
from ..middleware.logging import log_request
from ..middleware.rate_limit import api_rate_limits

config_bp = Blueprint('config', __name__)
config_schema = ConfigurationSchema()

@config_bp.route('/', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_config():
    """Ottiene la configurazione dell'utente corrente"""
    config = Configuration.query.filter_by(account_id=request.user_id).first()
    if not config:
        return APIResponse.error(message='Configurazione non trovata', status_code=404)
    
    return APIResponse.success(
        data=config_schema.dump(config),
        message='Configurazione recuperata con successo'
    )

@config_bp.route('/', methods=['POST', 'PUT'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def upsert_config():
    """Crea o aggiorna la configurazione"""
    config = Configuration.query.filter_by(account_id=request.user_id).first()
    
    try:
        data = config_schema.load(request.get_json())
        
        if config:
            # Aggiorna configurazione esistente
            for key, value in data.items():
                setattr(config, key, value)
            message = 'Configurazione aggiornata con successo'
        else:
            # Crea nuova configurazione
            config = Configuration(account_id=request.user_id, **data)
            db.session.add(config)
            message = 'Configurazione creata con successo'
        
        db.session.commit()
        
        return APIResponse.success(
            data=config_schema.dump(config),
            message=message
        )
        
    except ValidationError as e:
        return APIResponse.error(
            message='Errore di validazione',
            errors=e.messages,
            status_code=400
        )

@config_bp.route('/', methods=['PATCH'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def update_config_partial():
    """Aggiorna parzialmente la configurazione"""
    config = Configuration.query.filter_by(account_id=request.user_id).first()
    if not config:
        return APIResponse.error(message='Configurazione non trovata', status_code=404)
    
    try:
        data = request.get_json()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        db.session.commit()
        
        return APIResponse.success(
            data=config_schema.dump(config),
            message='Configurazione aggiornata con successo'
        )
        
    except ValidationError as e:
        return APIResponse.error(
            message='Errore di validazione',
            errors=e.messages,
            status_code=400
        )

@config_bp.route('/', methods=['DELETE'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def delete_config():
    """Elimina la configurazione"""
    config = Configuration.query.filter_by(account_id=request.user_id).first()
    if not config:
        return APIResponse.error(message='Configurazione non trovata', status_code=404)
    
    db.session.delete(config)
    db.session.commit()
    
    return APIResponse.success(message='Configurazione eliminata con successo')