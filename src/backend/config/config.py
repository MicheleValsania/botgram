"""
Configurazioni centralizzate per l'applicazione.
Include configurazioni per Flask, database, Instagram e altri servizi.
"""

import os
from datetime import timedelta

class InstagramConfig:
    """Configurazioni specifiche per Instagram."""
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
    """Configurazione base dell'applicazione."""
    # Flask
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///botgram.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Sicurezza
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_HEADERS = 'Content-Type'
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_KEY_PREFIX = 'botgram'
    RATELIMIT_HEADER_RETRY_AFTER = 'X-RateLimit-Retry-After'
    RATELIMIT_HEADER_REMAINING = 'X-RateLimit-Remaining'
    RATELIMIT_HEADER_RESET = 'X-RateLimit-Reset'
    
    # Instagram
    INSTAGRAM = InstagramConfig

class DevelopmentConfig(Config):
    """Configurazione per l'ambiente di sviluppo."""
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    RATELIMIT_ENABLED = True

class TestingConfig(Config):
    """Configurazione per l'ambiente di test."""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configurazione per l'ambiente di produzione."""
    # Tutte le impostazioni di sicurezza sono ereditate dalla classe base
    # Assicurarsi che tutte le variabili d'ambiente necessarie siano impostate
    pass

# Mapping degli ambienti alle configurazioni
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}