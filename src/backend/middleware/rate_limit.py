from flask import current_app, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from ..middleware.response import APIResponse

class RateLimiter:
    _instance = None
    _limiter = None

    @classmethod
    def get_instance(cls):
        """Gets the singleton instance of RateLimiter"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init_app(cls, app):
        """Initializes the rate limiter with Flask app"""
        if cls._limiter is None:
            app.config['RATELIMIT_HEADERS_ENABLED'] = True
            app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
            app.config['RATELIMIT_KEY_PREFIX'] = 'botgram'
            
            cls._limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=["1000 per day", "100 per hour"],
                storage_uri=app.config['RATELIMIT_STORAGE_URI']
            )
            
            @app.errorhandler(429)
            def ratelimit_handler(e):
                current_app.logger.warning(f"Rate limit exceeded: {str(e.description)}")
                return app.make_response(
                    (jsonify({
                        'success': False,
                        'message': f"Rate limit exceeded: {str(e.description)}"
                    }), 429)
                )

    @classmethod
    def get_limiter(cls):
        """Gets the Flask-Limiter instance"""
        if cls._limiter is None:
            raise RuntimeError("Rate limiter not initialized. Call init_app first.")
        return cls._limiter

    @classmethod
    def reset(cls):
        """Resets all rate limits (useful for testing)"""
        if cls._limiter and hasattr(cls._limiter, 'reset'):
            cls._limiter.reset()


def auth_rate_limits():
    """Decorator for authentication rate limits"""
    def decorator(f):
        limiter = RateLimiter.get_limiter()
        
        @limiter.limit("5 per minute", error_message="Too many authentication attempts")
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator

def api_rate_limits():
    """Decorator for general API rate limits"""
    def decorator(f):
        limiter = RateLimiter.get_limiter()
        
        @limiter.limit("10 per minute", error_message="Too many API requests")
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator

def instagram_rate_limits():
    """Decorator for Instagram-specific rate limits"""
    def decorator(f):
        limiter = RateLimiter.get_limiter()
        
        @limiter.limit("60 per hour", error_message="Too many Instagram actions")
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator