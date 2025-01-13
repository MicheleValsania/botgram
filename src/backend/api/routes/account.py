from flask import Blueprint, request
from marshmallow import ValidationError
from ...models.models import Account, db
from ...middleware.auth import token_required
from ...schemas.schemas import AccountSchema
from ...middleware.response import APIResponse, handle_api_errors
from ...middleware.logging import log_request
from ...middleware.rate_limit import api_rate_limits

account_bp = Blueprint('account', __name__)
account_schema = AccountSchema()

@account_bp.route('/', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_accounts():
    """Ottiene la lista degli account"""
    # Gestione della paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Query base
    query = Account.query
    
    # Esegue la query paginata
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Prepara i metadata
    meta = {
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages,
        'total_items': pagination.total
    }
    
    return APIResponse.success(
        data=account_schema.dump(pagination.items, many=True),
        message='Account recuperati con successo',
        meta=meta
    )

@account_bp.route('/<int:account_id>', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_account(account_id):
    """Ottiene i dettagli di un account specifico"""
    account = Account.query.get_or_404(account_id)
    return APIResponse.success(
        data=account_schema.dump(account),
        message='Account recuperato con successo'
    )

@account_bp.route('/<int:account_id>', methods=['PUT'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def update_account(account_id):
    """Aggiorna un account"""
    account = Account.query.get_or_404(account_id)
    
    try:
        data = account_schema.load(request.get_json(), partial=True)
        
        for key, value in data.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        db.session.commit()
        
        return APIResponse.success(
            data=account_schema.dump(account),
            message='Account aggiornato con successo'
        )
        
    except ValidationError as e:
        return APIResponse.error(
            message='Errore di validazione',
            errors=e.messages,
            status_code=400
        )

@account_bp.route('/<int:account_id>', methods=['DELETE'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def delete_account(account_id):
    """Elimina un account"""
    account = Account.query.get_or_404(account_id)
    
    # Soft delete: imposta is_active a False invece di eliminare
    account.is_active = False
    db.session.commit()
    
    return APIResponse.success(
        message='Account disattivato con successo'
    )