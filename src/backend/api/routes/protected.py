"""
Route protette per testing.
"""

from flask import Blueprint
from ...middleware.auth import token_required
from ...middleware.response import APIResponse

protected_bp = Blueprint('protected', __name__)

@protected_bp.route('', methods=['GET'])
@token_required
def protected():
    """Route protetta di test."""
    return APIResponse.success(message='Accesso consentito')
