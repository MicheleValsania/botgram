from flask import Blueprint


# Create the main API blueprint
api = Blueprint('api', __name__)

# Import all route blueprints
from .routes.auth import auth_bp
from .routes.account import account_bp
from .routes.config import config_bp
from .routes.interaction import interaction_bp

# Register all blueprints with their prefixes
api.register_blueprint(auth_bp, url_prefix='/auth')
api.register_blueprint(account_bp, url_prefix='/accounts')
api.register_blueprint(config_bp, url_prefix='/config')
api.register_blueprint(interaction_bp, url_prefix='/interactions')
