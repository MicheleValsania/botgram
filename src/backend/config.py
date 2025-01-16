"""
Configurazioni per l'applicazione Flask e Instagram
"""

class InstagramConfig:
    """Configurazioni specifiche per Instagram"""
    # Limiti giornalieri per le azioni
    FOLLOW_LIMIT_PER_DAY = 100
    LIKE_LIMIT_PER_DAY = 500
    COMMENT_LIMIT_PER_DAY = 50
    
    # Configurazione sessione
    SESSION_EXPIRY_HOURS = 24
    
    # Intervalli minimi tra le azioni (in secondi)
    MIN_DELAY_BETWEEN_ACTIONS = 30
    MIN_DELAY_BETWEEN_FOLLOWS = 60
    MIN_DELAY_BETWEEN_LIKES = 30
    MIN_DELAY_BETWEEN_COMMENTS = 120
    
    # Configurazioni di sicurezza
    MAX_ACTIONS_PER_SESSION = 1000
    COOLDOWN_HOURS = 24
    
    # Headers e User Agent
    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # Endpoint URLs
    BASE_URL = 'https://www.instagram.com'
    LOGIN_URL = f'{BASE_URL}/accounts/login/ajax/'
    LOGOUT_URL = f'{BASE_URL}/accounts/logout/'

class Config:
    """Configurazione base"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///botgram.db'
    SECRET_KEY = 'dev-key'
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_KEY_PREFIX = 'botgram'
    RATELIMIT_HEADER_RETRY_AFTER = 'X-RateLimit-Retry-After'
    RATELIMIT_HEADER_REMAINING = 'X-RateLimit-Remaining'
    RATELIMIT_HEADER_RESET = 'X-RateLimit-Reset'
    
    # Instagram configuration
    INSTAGRAM = InstagramConfig

class DevelopmentConfig(Config):
    """Configurazione per l'ambiente di sviluppo"""
    DEBUG = True
    ENV = 'development'

class TestingConfig(Config):
    """Configurazione per l'ambiente di test"""
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    """Configurazione per l'ambiente di produzione"""
    ENV = 'production'
