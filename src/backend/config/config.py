import os
from datetime import timedelta

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