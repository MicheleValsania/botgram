# src/backend/api/routes/instagram.py

from flask import Blueprint, request, g
from ...middleware.auth import token_required
from ...middleware.rate_limit import instagram_rate_limits
from ...middleware.response import APIResponse
from ...middleware.logging import log_request

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/action', methods=['POST'])
@token_required
@instagram_rate_limits()
@log_request()
def instagram_action():
    """Endpoint per le azioni Instagram"""
    try:
        action_type = request.json.get('type')
        media_id = request.json.get('media_id')
        
        # Qui implementeremo la logica per le diverse azioni
        return APIResponse.success(
            data={'action': action_type, 'media_id': media_id},
            message='Azione Instagram eseguita con successo'
        )
        
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante l'esecuzione dell'azione Instagram: {str(e)}",
            status_code=500
        )