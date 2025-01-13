from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps

class RateLimiter:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Limiter(
                key_func=get_remote_address,
                default_limits=["200 per day", "50 per hour"]
            )
        return cls._instance

    @classmethod
    def init_app(cls, app):
        limiter = cls.get_instance()
        limiter.init_app(app)

        @app.errorhandler(429)
        def ratelimit_handler(e):
            return {
                "success": False,
                "error": "ratelimit exceeded",
                "message": str(e.description)
            }, 429

# src/backend/middleware/rate_limit.py

def auth_rate_limits():
    def decorator(f):
        limiter = RateLimiter.get_instance()
        # Usa direttamente il limiter.limit senza nesting
        @limiter.limit("5 per minute")
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator

def api_rate_limits():
    """Decorator per i limiti di rate sulle API generiche"""
    def decorator(f):
        limiter = RateLimiter.get_instance()
        
        return limiter.limit("1000 per day")(
               limiter.limit("100 per hour")(
               limiter.limit("10 per minute")(f)))
    return decorator

def instagram_rate_limits():
    """Decorator per i limiti di rate sulle operazioni Instagram"""
    def decorator(f):
        limiter = RateLimiter.get_instance()
        
        return limiter.limit("60 per hour")(
               limiter.limit("500 per day")(f))
    return decorator