from flask import Blueprint
from .routes.auth import auth_bp
from .routes.account import account_bp
from .routes.config import config_bp
from .routes.interaction import interaction_bp
from .routes.instagram import instagram_bp

# Create the main API blueprint
api = Blueprint('api', __name__)

# Register all blueprints with their prefixes
api.register_blueprint(auth_bp, url_prefix='/auth')
api.register_blueprint(account_bp, url_prefix='/accounts')
api.register_blueprint(config_bp, url_prefix='/config')
api.register_blueprint(interaction_bp, url_prefix='/interactions')
api.register_blueprint(instagram_bp, url_prefix='/instagram')