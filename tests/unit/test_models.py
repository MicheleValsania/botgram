# tests/unit/test_models.py
import pytest
from datetime import datetime
from src.backend.models.models import Account, Configuration
from src.backend.config.database import db

def test_new_account(app):
    with app.app_context():
        account = Account(
            username='testuser',
            password_hash='hashedpassword',
            email='test@example.com'
        )
        db.session.add(account)
        db.session.commit()

        assert account.username == 'testuser'
        assert account.email == 'test@example.com'
        assert account.password_hash == 'hashedpassword'
        assert account.is_active == True
        assert isinstance(account.created_at, datetime)

def test_account_configuration_relationship(app):
    with app.app_context():
        account = Account(
            username='testuser',
            password_hash='hashedpassword',
            email='test@example.com'
        )
        db.session.add(account)
        db.session.commit()

        config = Configuration(
            account_id=account.id,
            daily_like_limit=50,
            daily_follow_limit=20,
            min_delay=2.0,
            max_delay=5.0
        )
        db.session.add(config)
        db.session.commit()

        assert account.configurations is not None
        assert account.configurations.daily_like_limit == 50
        assert config.account.username == 'testuser'