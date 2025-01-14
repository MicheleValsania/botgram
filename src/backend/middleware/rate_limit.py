from flask import current_app, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from ..middleware.response import APIResponse  
class RateLimiter:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Limiter(
                get_remote_address,
                app=current_app,
                default_limits=["1000 per day", "100 per hour"],
                storage_uri="memory://",
            )
        return cls._instance

    @classmethod
    def init_app(cls, app):
        limiter = cls.get_instance()
        limiter.init_app(app)

        app.config['RATELIMIT_HEADERS_ENABLED'] = True 
        # In src/backend/middleware/rate_limit.py
        @app.errorhandler(429)
        def ratelimit_handler(e):
            app.logger.warning(f"Rate limit exceeded: {str(e.description)}")
            return APIResponse.error(
                message=f"Rate limit exceeded: {str(e.description)}",
                status_code=429
            )

def auth_rate_limits(f=None):
    """Decorator per limiti sulle operazioni di autenticazione"""
    if f is None:
        return auth_rate_limits
        
    limiter = RateLimiter.get_instance()
    
    @limiter.limit(
        "5 per minute", 
        methods=["POST"],
        error_message="Troppi tentativi, riprova più tardi",
        key_func=get_remote_address
    )
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped

def api_rate_limits(f=None):
    """Decorator per limiti sulle API generiche"""
    if f is None:
        return api_rate_limits
        
    limiter = RateLimiter.get_instance()
    
    # Limiti multipli: giornaliero, orario e al minuto
    @limiter.limit("1000 per day")
    @limiter.limit("100 per hour")
    @limiter.limit("10 per minute")
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped

def instagram_rate_limits(f=None):
    """Decorator per limiti sulle operazioni Instagram"""
    if f is None:
        return instagram_rate_limits
        
    limiter = RateLimiter.get_instance()
    
    # Limiti specifici per le azioni Instagram
    @limiter.limit("500 per day")
    @limiter.limit("60 per hour")
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped