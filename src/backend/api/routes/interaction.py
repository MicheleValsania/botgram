from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import desc
from ...models.models import InteractionLog, db
from ...middleware.auth import token_required
from ...schemas.schemas import InteractionLogSchema
from ...middleware.response import APIResponse, handle_api_errors
from ...middleware.logging import log_request
from ...middleware.rate_limit import api_rate_limits

interaction_bp = Blueprint('interaction', __name__)
interaction_schema = InteractionLogSchema()
interactions_schema = InteractionLogSchema(many=True)

@interaction_bp.route('/', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_interactions():
    """Ottiene la lista delle interazioni"""
    # Gestione della paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Gestione dei filtri
    interaction_type = request.args.get('type')
    status = request.args.get('status')
    target_username = request.args.get('target_username')
    
    # Query base
    query = InteractionLog.query.filter_by(account_id=request.user_id)
    
    # Applica i filtri se presenti
    if interaction_type:
        query = query.filter_by(interaction_type=interaction_type)
    if status:
        query = query.filter_by(status=status)
    if target_username:
        query = query.filter_by(target_username=target_username)
    
    # Ordina per data decrescente
    query = query.order_by(desc(InteractionLog.created_at))
    
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
        data=interactions_schema.dump(pagination.items),
        message='Interazioni recuperate con successo',
        meta=meta
    )

@interaction_bp.route('/<int:interaction_id>', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_interaction(interaction_id):
    """Ottiene i dettagli di una specifica interazione"""
    interaction = InteractionLog.query.filter_by(
        id=interaction_id,
        account_id=request.user_id
    ).first()
    
    if not interaction:
        return APIResponse.error(message='Interazione non trovata', status_code=404)
    
    return APIResponse.success(
        data=interaction_schema.dump(interaction),
        message='Dettagli interazione recuperati con successo'
    )

@interaction_bp.route('/', methods=['POST'])
@token_required
@api_rate_limits()
@log_request()
@handle_api_errors
def create_interaction():
    """Registra una nuova interazione"""
    try:
        data = interaction_schema.load(request.get_json())
        
        interaction = InteractionLog(
            account_id=request.user_id,
            **data
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return APIResponse.success(
            data=interaction_schema.dump(interaction),
            message='Interazione registrata con successo',
            status_code=201
        )
        
    except ValidationError as e:
        return APIResponse.error(
            message='Errore di validazione',
            errors=e.messages,
            status_code=400
        )

@interaction_bp.route('/stats', methods=['GET'])
@token_required
@log_request()
@handle_api_errors
def get_interaction_stats():
    """Ottiene le statistiche delle interazioni"""
    from sqlalchemy import func
    
    # Statistiche per tipo di interazione
    stats_by_type = db.session.query(
        InteractionLog.interaction_type,
        func.count().label('total'),
        func.sum(case((InteractionLog.status == 'success', 1), else_=0)).label('successful')
    ).filter_by(account_id=request.user_id).group_by(
        InteractionLog.interaction_type
    ).all()
    
    # Formatta le statistiche
    stats = {
        'by_type': [
            {
                'type': stat.interaction_type,
                'total': stat.total,
                'successful': stat.successful or 0,
                'success_rate': round((stat.successful or 0) / stat.total * 100, 2)
            }
            for stat in stats_by_type
        ]
    }
    
    return APIResponse.success(
        data=stats,
        message='Statistiche interazioni recuperate con successo'
    )