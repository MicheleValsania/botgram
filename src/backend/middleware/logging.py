import logging
from logging.config import dictConfig
from flask import request, g
import time
from functools import wraps
from uuid import uuid4
import json
from datetime import datetime
import os



# src/backend/middleware/logging.py
def is_testing():
    """Check if we're running in test mode."""
    try:
        from flask import current_app
        return current_app.config.get('TESTING', False)
    except RuntimeError:
        return False
    
def setup_logger(app):
    """Configurazione del logger"""
    
    # Crea la directory logs se non esiste
    log_dir = os.path.join(app.root_path, '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configura log handlers in base all'ambiente
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['request_id']
        }
    }
    
    # Aggiungi file handlers solo se non siamo in testing
    if not app.config.get('TESTING', False):
        handlers.update({
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'api.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'detailed',
                'filters': ['request_id']
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'formatter': 'detailed',
                'filters': ['request_id'],
                'level': 'ERROR'
            }
        })

    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] [%(request_id)s] [%(name)s:%(lineno)d] %(message)s'
            }
        },
        'filters': {
            'request_id': {
                '()': 'src.backend.middleware.logging.RequestIdFilter'
            }
        },
        'handlers': handlers,
        'root': {
            'level': 'DEBUG' if app.debug else 'INFO',
            'handlers': list(handlers.keys())
        }
    })

class RequestIdFilter(logging.Filter):
    """Filtro per aggiungere request_id ai log"""
    def filter(self, record):
        if is_testing():
            record.request_id = 'test'
            return True
        try:
            record.request_id = getattr(g, 'request_id', 'no_request_id')
        except RuntimeError:
            record.request_id = 'no_context'
        return True

def log_request():
    """Middleware per loggare le richieste HTTP"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Genera un ID univoco per la richiesta
            g.request_id = str(uuid4())
            
            # Prepara i dati della richiesta per il logging
            request_data = {
                'method': request.method,
                'url': request.full_path,
                'headers': dict(request.headers),
                'body': request.get_json(silent=True) if request.is_json else None
            }
            
            # Crea una copia dei dati per il logging
            log_data = {
                'method': request_data['method'],
                'url': request_data['url'],
                'headers': dict(request_data['headers']),
                'body': dict(request_data['body']) if request_data['body'] else None
            }
            
            # Rimuovi informazioni sensibili dalla copia per il logging
            if log_data['body'] and 'password' in log_data['body']:
                log_data['body']['password'] = '[REDACTED]'
            if 'Authorization' in log_data['headers']:
                log_data['headers']['Authorization'] = '[REDACTED]'
            
            # Log della richiesta
            logging.info(f"Incoming request: {json.dumps(log_data)}")
            
            # Misura il tempo di risposta
            start_time = time.time()
            
            try:
                response = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log della risposta
                response_data = {
                    'status_code': getattr(response, 'status_code', None),
                    'duration': f"{duration:.3f}s"
                }
                logging.info(f"Request completed: {json.dumps(response_data)}")
                
                return response
            
            except Exception as e:
                duration = time.time() - start_time
                
                # Log dell'errore
                error_data = {
                    'error': str(e),
                    'duration': f"{duration:.3f}s"
                }
                logging.error(f"Request failed: {json.dumps(error_data)}", exc_info=True)
                raise
            
        return wrapped
    return decorator
def init_logging(app):
    """Inizializza il sistema di logging"""
    setup_logger(app)
    
    # Log di avvio applicazione
    logging.info(f"Application started at {datetime.utcnow().isoformat()}")
    
    # Log di tutte le richieste
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid4())
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logging.info(f"Request processed in {duration:.3f}s")
        return response