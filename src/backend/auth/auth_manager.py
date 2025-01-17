from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.models import Account

login_manager = LoginManager()
jwt = JWTManager()

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

def init_auth(app):
    """Initialize authentication systems"""
    login_manager.init_app(app)
    jwt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']  # Use the same secret key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days

def create_user(username, email, password):
    """Create a new user"""
    hashed_password = generate_password_hash(password)
    user = Account(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    return user

def verify_password(user, password):
    """Verify user password"""
    return check_password_hash(user.password_hash, password)
