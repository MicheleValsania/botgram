from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app, request, jsonify

class RateLimiter:
    _instance = None
    _limiter = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init_app(cls, app):
        """Inizializza il rate limiter con l'app Flask"""
        # Configura il rate limiter solo se non è disabilitato
        if not app.config.get('TESTING', False):
            app.config['RATELIMIT_HEADERS_ENABLED'] = True
            app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
            app.config['RATELIMIT_KEY_PREFIX'] = 'botgram'
            app.config['RATELIMIT_HEADER_RETRY_AFTER'] = 'X-RateLimit-Retry-After'
            app.config['RATELIMIT_HEADER_REMAINING'] = 'X-RateLimit-Remaining'
            app.config['RATELIMIT_HEADER_RESET'] = 'X-RateLimit-Reset'
            
            cls._limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=["1000 per day", "100 per hour"],
                storage_uri=app.config['RATELIMIT_STORAGE_URI']
            )
            
            @app.errorhandler(429)
            def ratelimit_handler(e):
                from ..middleware.response import APIResponse
                return APIResponse.error(
                    message=str(e.description),
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED"
                )
        else:
            # In ambiente di test, crea un limiter fittizio
            cls._limiter = type('DummyLimiter', (), {
                'storage': type('DummyStorage', (), {
                    'get': lambda *args: 0,
                    'incr': lambda *args: None,
                    'reset': lambda *args: None
                })()
            })()

    @classmethod
    def get_limiter(cls):
        """Ottiene l'istanza del rate limiter"""
        if cls._limiter is None:
            raise RuntimeError("Rate limiter not initialized. Call init_app first.")
        return cls._limiter

    @classmethod
    def reset(cls):
        """Resetta tutti i rate limits"""
        if cls._limiter and hasattr(cls._limiter, 'reset'):
            cls._limiter.reset()

def handle_rate_limit_error(e):
    """Gestisce gli errori di rate limit in modo uniforme"""
    current_app.logger.warning(f"Rate limit exceeded: {str(e.description)}")
    from ..middleware.response import APIResponse
    return APIResponse.error(
        message=str(e.description),
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    )

def auth_rate_limits():
    """Decorator per i limiti di autenticazione"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Se siamo in ambiente di test, ignora il rate limiting
            if current_app.config.get('TESTING', False):
                return f(*args, **kwargs)
            
            limiter = RateLimiter.get_limiter()
            key = request.remote_addr
            
            # Verifica se l'indirizzo IP ha superato il limite
            current = limiter.storage.get(key) or 0
            if current and int(current) >= 5:
                from ..middleware.response import APIResponse
                return APIResponse.error(
                    message='Rate limit exceeded for authentication endpoint',
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            
            # Esegui la funzione
            response = f(*args, **kwargs)
            
            # Se la risposta è una tupla, estrai il primo elemento che è l'oggetto response
            if isinstance(response, tuple):
                response_obj = response[0]
                status_code = response[1]
            else:
                response_obj = response
                status_code = response.status_code
            
            # Incrementa il contatore per tutte le richieste di autenticazione
            # incluse quelle fallite (401)
            limiter.storage.incr(key, 60)
            
            return response
        return wrapped
    return decorator

def api_rate_limits():
    """Decorator per i limiti delle API generiche"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Se siamo in ambiente di test, ignora il rate limiting
            if current_app.config.get('TESTING', False):
                return f(*args, **kwargs)
            
            limiter = RateLimiter.get_limiter()
            key = request.remote_addr
            
            # Verifica se l'indirizzo IP ha superato il limite
            current = limiter.storage.get(key) or 0
            if current and int(current) >= 100:
                from ..middleware.response import APIResponse
                return APIResponse.error(
                    message='Rate limit exceeded for API endpoint',
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            
            # Esegui la funzione
            response = f(*args, **kwargs)
            
            # Se la risposta è una tupla, estrai il primo elemento che è l'oggetto response
            if isinstance(response, tuple):
                response_obj = response[0]
                status_code = response[1]
            else:
                response_obj = response
                status_code = response.status_code
            
            # Incrementa il contatore solo per le richieste riuscite
            if status_code < 400:
                limiter.storage.incr(key, 60)
            
            return response
        return wrapped
    return decorator

def instagram_rate_limits():
    """Decorator per i limiti specifici di Instagram"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            limiter = RateLimiter.get_limiter()
            limit_decorator = limiter.limit("60 per hour",
                                         error_message="Rate limit exceeded for Instagram endpoint")
            try:
                return limit_decorator(f)(*args, **kwargs)
            except Exception as e:
                return handle_rate_limit_error(e)
        return wrapped
    return decorator