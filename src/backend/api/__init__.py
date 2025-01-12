from flask import Blueprint

# Create the main API blueprint
api = Blueprint('api', __name__)

# Import routes
from . import routes
from . import auth

# Register the auth blueprint
from .auth import auth_bp
api.register_blueprint(auth_bp, url_prefix='/auth')