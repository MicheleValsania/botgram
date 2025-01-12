from flask import Blueprint

# Crea il blueprint principale
api = Blueprint('api', __name__)

# Importa i blueprint delle route
from .auth import auth_bp
from .account import account_bp
from .config import config_bp
from .interaction import interaction_bp

# Registra i blueprint con i loro prefissi
api.register_blueprint(auth_bp, url_prefix='/auth')
api.register_blueprint(account_bp, url_prefix='/accounts')
api.register_blueprint(config_bp, url_prefix='/config')
api.register_blueprint(interaction_bp, url_prefix='/interactions')