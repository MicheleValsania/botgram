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
                "error": "ratelimit exceeded",
                "message": str(e.description)
            }, 429

# src/backend/middleware/rate_limit.py

from functools import wraps

def auth_rate_limits():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            limiter = RateLimiter.get_instance()
            limits = ["5 per minute", "20 per hour", "100 per day"]
            
            # Applica i limiti dinamicamente
            decorated = f
            for limit in limits:
                decorated = limiter.limit(limit)(decorated)
            
            return decorated(*args, **kwargs)
        return wrapped
    return decorator

def api_rate_limits():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            limiter = RateLimiter.get_instance()
            limits = ["1000 per day", "100 per hour", "10 per minute"]
            
            # Applica i limiti dinamicamente
            for limit in limits:
                decorated = limiter.limit(limit)(f)
                f = decorated
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def instagram_rate_limits():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            limiter = RateLimiter.get_instance()
            limits = ["60 per hour", "500 per day"]
            
            # Applica i limiti dinamicamente
            for limit in limits:
                decorated = limiter.limit(limit)(f)
                f = decorated
            
            return f(*args, **kwargs)
        return wrapped
    return decorator