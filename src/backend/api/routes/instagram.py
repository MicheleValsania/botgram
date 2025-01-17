"""Instagram API routes."""
from flask import Blueprint, request, jsonify
from ...middleware.auth import token_required
from ...middleware.response import APIResponse
from ...instagram.session import InstagramSessionManager
from ...instagram.client import InstagramClient
from ...instagram.schemas import (
    FollowSchema, LikeSchema, CommentSchema, SessionSchema
)
from ...config import InstagramConfig

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/session', methods=['POST'])
@token_required
def create_session():
    """Create a new Instagram session."""
    data = request.get_json()
    
    # Validate request data
    errors = SessionSchema().validate(data)
    if errors:
        return APIResponse.error('Invalid request data', errors=errors)
    
    # Create session
    session = InstagramSessionManager.create_session(
        username=data['username'],
        session_id=data['session_id'],
        cookies=data['cookies'],
        user_agent=data['user_agent']
    )
    
    return APIResponse.success({
        'session_created': True,
        'username': session.username
    })

@instagram_bp.route('/follow', methods=['POST'])
@token_required
def follow_user():
    """Follow a user on Instagram."""
    data = request.get_json()
    
    # Validate request data
    errors = FollowSchema().validate(data)
    if errors:
        return APIResponse.error('Invalid request data', errors=errors)
    
    username = data['username']
    target_user_id = data['target_user_id']
    
    # Get user session
    session = InstagramSessionManager.get_session(username)
    if not session or not session.is_valid:
        return APIResponse.error('No valid session found', error_code='INVALID_SESSION', status_code=401)
    
    # Check rate limits
    if session.rate_limits['follow'] <= 0:
        return APIResponse.error('Rate limit exceeded', error_code='RATE_LIMIT_EXCEEDED', status_code=429)
    
    # Create Instagram client
    client = InstagramClient(username=username)
    
    # Follow user
    response, status_code = client.follow_user(target_user_id)
    if status_code != 200:
        return APIResponse.error('Failed to follow user', error_code='FOLLOW_ERROR', status_code=status_code)
    
    # Update rate limits
    session.rate_limits['follow'] -= 1
    
    return APIResponse.success({'status': response.get('status', 'ok')})

@instagram_bp.route('/like', methods=['POST'])
@token_required
def like_post():
    """Like a post on Instagram."""
    data = request.get_json()
    
    # Validate request data
    errors = LikeSchema().validate(data)
    if errors:
        return APIResponse.error('Invalid request data', errors=errors)
    
    username = data['username']
    media_id = data['media_id']
    
    # Get user session
    session = InstagramSessionManager.get_session(username)
    if not session or not session.is_valid:
        return APIResponse.error('No valid session found', error_code='INVALID_SESSION', status_code=401)
    
    # Check rate limits
    if session.rate_limits['like'] <= 0:
        return APIResponse.error('Rate limit exceeded', error_code='RATE_LIMIT_EXCEEDED', status_code=429)
    
    # Create Instagram client
    client = InstagramClient(username=username)
    
    # Like post
    response, status_code = client.like_post(media_id)
    if status_code != 200:
        return APIResponse.error('Failed to like post', error_code='LIKE_ERROR', status_code=status_code)
    
    # Update rate limits
    session.rate_limits['like'] -= 1
    
    return APIResponse.success({'status': response.get('status', 'ok')})

@instagram_bp.route('/comment', methods=['POST'])
@token_required
def comment_post():
    """Comment on a post on Instagram."""
    data = request.get_json()
    
    # Validate request data
    errors = CommentSchema().validate(data)
    if errors:
        return APIResponse.error('Invalid request data', errors=errors)
    
    username = data['username']
    media_id = data['media_id']
    comment_text = data['comment_text']
    
    # Get user session
    session = InstagramSessionManager.get_session(username)
    if not session or not session.is_valid:
        return APIResponse.error('No valid session found', error_code='INVALID_SESSION', status_code=401)
    
    # Check rate limits
    if session.rate_limits['comment'] <= 0:
        return APIResponse.error('Rate limit exceeded', error_code='RATE_LIMIT_EXCEEDED', status_code=429)
    
    # Create Instagram client
    client = InstagramClient(username=username)
    
    # Comment on post
    response, status_code = client.comment_post(media_id, comment_text)
    if status_code != 200:
        return APIResponse.error('Failed to comment on post', error_code='COMMENT_ERROR', status_code=status_code)
    
    # Update rate limits
    session.rate_limits['comment'] -= 1
    
    return APIResponse.success({'status': response.get('status', 'ok')})

@instagram_bp.route('/session/<username>', methods=['DELETE'])
@token_required
def end_session(username):
    """End an Instagram session."""
    # Get user session
    session = InstagramSessionManager.get_session(username)
    if not session or not session.is_valid:
        return APIResponse.error('No valid session found', error_code='INVALID_SESSION', status_code=401)
    
    # Create Instagram client and logout
    client = InstagramClient(username=username)
    response, status_code = client.logout()
    
    if status_code != 200:
        return APIResponse.error('Failed to end session', error_code='LOGOUT_ERROR', status_code=status_code)
    
    return APIResponse.success({'status': response.get('status', 'ok')})

@instagram_bp.route('/limits/<username>', methods=['GET'])
@token_required
def get_limits(username):
    """Get rate limits for a user."""
    session = InstagramSessionManager.get_session(username)
    if not session or not session.is_valid:
        return APIResponse.error('No valid session found', error_code='INVALID_SESSION', status_code=401)
    
    return APIResponse.success({
        'limits': session.rate_limits,
        'username': username
    })