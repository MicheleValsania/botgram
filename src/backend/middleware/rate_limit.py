from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from flask import request, jsonify
import redis
import json

class RateLimiter:
    def __init__(self, app=None, redis_url=None):
        self.limiter = None
        if app is not None:
            self.init_app(app, redis_url)

    def init_app(self, app, redis_url=None):
        """Inizializza il rate limiter con l'app Flask"""
        
        # Configura Redis come storage backend se fornito
        storage_uri = redis_url or 'memory://'
        
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,  # Default key function
            storage_uri=storage_uri,
            strategy="fixed-window",  # Strategia di rate limiting
            default_limits=["200 per day", "50 per hour"]  # Limiti di default
        )

        # Aggiungi handler per errori di rate limit
        @app.errorhandler(429)
        def ratelimit_handler(e):
            return jsonify({
                "error": "ratelimit exceeded",
                "message": str(e.description),
                "retry_after": int(e.retry_after)
            }), 429

    def limit_requests(self, limits):
        """Decorator per applicare limiti specifici agli endpoint"""
        def decorator(f):
            @wraps(f)
            @self.limiter.limit(limits)
            def wrapped(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapped
        return decorator

    def exempt(self):
        """Decorator per escludere un endpoint dal rate limiting"""
        return self.limiter.exempt

def api_rate_limits():
    """Decorator per limiti specifici per le API"""
    return RateLimiter.limit_requests([
        "1000 per day",  # Limite giornaliero
        "100 per hour",  # Limite orario
        "10 per minute"  # Limite al minuto
    ])

def auth_rate_limits():
    """Decorator per limiti specifici per l'autenticazione"""
    return RateLimiter.limit_requests([
        "5 per minute",   # Protezione contro bruteforce
        "20 per hour",    # Limite orario per tentativi
        "100 per day"     # Limite giornaliero totale
    ])

def instagram_rate_limits():
    """Decorator per limiti specifici per le interazioni Instagram"""
    return RateLimiter.limit_requests([
        "60 per hour",    # Limite orario per le azioni Instagram
        "500 per day"     # Limite giornaliero totale
    ])