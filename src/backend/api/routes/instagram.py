# src/backend/api/routes/instagram.py

from flask import Blueprint, request, g
from marshmallow import ValidationError

from ...middleware.auth import token_required
from ...middleware.rate_limit import instagram_rate_limits
from ...middleware.response import APIResponse
from ...middleware.logging import log_request
from ...instagram.client import InstagramClient
from ...instagram.session import InstagramSessionManager
from ...schemas.instagram_schemas import (
    InstagramFollowSchema, 
    InstagramLikeSchema,
    InstagramCommentSchema,
    InstagramSessionSchema
)

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/session', methods=['POST'])
@token_required
@log_request()
def create_session():
    """Crea una nuova sessione Instagram."""
    try:
        # Valida i dati della sessione
        schema = InstagramSessionSchema()
        data = schema.load(request.json)
        
        # Crea la sessione
        session = InstagramSessionManager.create_session(
            username=data['username'],
            session_id=data['session_id'],
            cookies=data['cookies'],
            user_agent=data['user_agent']
        )
        
        return APIResponse.success(
            data={'session_created': True},
            message='Sessione Instagram creata con successo'
        )
        
    except ValidationError as e:
        return APIResponse.error(
            message='Dati sessione non validi',
            error_code='VALIDATION_ERROR',
            errors=e.messages,
            status_code=400
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante la creazione della sessione: {str(e)}",
            status_code=500
        )

@instagram_bp.route('/follow', methods=['POST'])
@token_required
@instagram_rate_limits()
@log_request()
def follow_user():
    """Segue un utente su Instagram."""
    try:
        # Valida i dati della richiesta
        schema = InstagramFollowSchema()
        data = schema.load(request.json)
        
        # Crea il client Instagram
        client = InstagramClient(data['username'])
        
        # Esegue l'azione
        response, status_code = client.follow_user(data['target_user_id'])
        return response, status_code
        
    except ValidationError as e:
        return APIResponse.error(
            message='Dati non validi',
            error_code='VALIDATION_ERROR',
            errors=e.messages,
            status_code=400
        )
    except ValueError as e:
        return APIResponse.error(
            message=str(e),
            error_code='SESSION_ERROR',
            status_code=401
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante il follow: {str(e)}",
            status_code=500
        )

@instagram_bp.route('/like', methods=['POST'])
@token_required
@instagram_rate_limits()
@log_request()
def like_post():
    """Mette like a un post su Instagram."""
    try:
        # Valida i dati della richiesta
        schema = InstagramLikeSchema()
        data = schema.load(request.json)
        
        # Crea il client Instagram
        client = InstagramClient(data['username'])
        
        # Esegue l'azione
        response, status_code = client.like_post(data['media_id'])
        return response, status_code
        
    except ValidationError as e:
        return APIResponse.error(
            message='Dati non validi',
            error_code='VALIDATION_ERROR',
            errors=e.messages,
            status_code=400
        )
    except ValueError as e:
        return APIResponse.error(
            message=str(e),
            error_code='SESSION_ERROR',
            status_code=401
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante il like: {str(e)}",
            status_code=500
        )

@instagram_bp.route('/comment', methods=['POST'])
@token_required
@instagram_rate_limits()
@log_request()
def comment_post():
    """Commenta un post su Instagram."""
    try:
        # Valida i dati della richiesta
        schema = InstagramCommentSchema()
        data = schema.load(request.json)
        
        # Crea il client Instagram
        client = InstagramClient(data['username'])
        
        # Esegue l'azione
        response, status_code = client.comment_post(
            data['media_id'],
            data['comment_text']
        )
        return response, status_code
        
    except ValidationError as e:
        return APIResponse.error(
            message='Dati non validi',
            error_code='VALIDATION_ERROR',
            errors=e.messages,
            status_code=400
        )
    except ValueError as e:
        return APIResponse.error(
            message=str(e),
            error_code='SESSION_ERROR',
            status_code=401
        )
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante il commento: {str(e)}",
            status_code=500
        )

@instagram_bp.route('/session/<username>', methods=['DELETE'])
@token_required
@log_request()
def end_session(username):
    """Termina una sessione Instagram."""
    try:
        # Verifica che la sessione esista
        session = InstagramSessionManager.get_session(username)
        if not session:
            return APIResponse.error(
                message='Sessione non trovata',
                error_code='SESSION_NOT_FOUND',
                status_code=404
            )
        
        # Crea il client e effettua il logout
        client = InstagramClient(username, session)
        client.logout()
        
        return APIResponse.success(
            message='Sessione terminata con successo'
        )
        
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante la chiusura della sessione: {str(e)}",
            status_code=500
        )

@instagram_bp.route('/limits/<username>', methods=['GET'])
@token_required
@log_request()
def get_limits(username):
    """Ottiene i limiti rimanenti per un utente."""
    try:
        session = InstagramSessionManager.get_session(username)
        if not session:
            return APIResponse.error(
                message='Sessione non trovata',
                error_code='SESSION_NOT_FOUND',
                status_code=404
            )
        
        limits = session.get_remaining_limits()
        return APIResponse.success(
            data={'limits': limits},
            message='Limiti recuperati con successo'
        )
        
    except Exception as e:
        return APIResponse.error(
            message=f"Errore durante il recupero dei limiti: {str(e)}",
            status_code=500
        )