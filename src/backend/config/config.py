import os
from datetime import timedelta

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
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///botgram.db')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    CORS_HEADERS = 'Content-Type'
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Instagram configuration
    INSTAGRAM = InstagramConfig

class DevelopmentConfig(Config):
    """Configurazione per sviluppo"""
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Configurazione per testing"""
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configurazione per produzione"""
    DEBUG = False
    ENV = 'production'
    SQLALCHEMY_ECHO = False
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Override necessario in produzione
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Configurazioni di sicurezza aggiuntive
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True