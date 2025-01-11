# src/backend/config/database.py
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import os

db = SQLAlchemy()

def init_db(app):
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///botgram.db'  # fallback to SQLite for development
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Import models here to avoid circular imports
    from ..models.models import Account, Configuration, InteractionLog, TargetProfile
    
    # Create tables
    with app.app_context():
        db.create_all()