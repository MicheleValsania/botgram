# tests/unit/test_services.py
import pytest
from datetime import datetime, UTC
from src.backend.models.models import Account, InteractionLog, Configuration
from src.backend.config.database import db
from sqlalchemy import func

def test_create_interaction_log(app, test_account):
    """Test creation of interaction log"""
    with app.app_context():
        # Uso di db.session.get invece di Query.get
        account = db.session.get(Account, test_account.id)
        
        log = InteractionLog(
            account_id=account.id,
            interaction_type='follow',
            target_username='target_user',
            status='success',
            created_at=datetime.now(UTC)
        )
        db.session.add(log)
        db.session.commit()

        # Verify log was created
        fetched_log = InteractionLog.query.filter_by(
            account_id=account.id).first()
        assert fetched_log is not None
        assert fetched_log.interaction_type == 'follow'
        assert fetched_log.target_username == 'target_user'
        assert fetched_log.status == 'success'

def test_account_configuration_limits(app, test_account):
    """Test configuration limits for account"""
    with app.app_context():
        # Uso di db.session.get invece di Query.get
        account = db.session.get(Account, test_account.id)
        
        config = Configuration(
            account_id=account.id,
            daily_like_limit=50,
            daily_follow_limit=20,
            daily_unfollow_limit=10,
            min_delay=2.0,
            max_delay=5.0,
            target_hashtags=['tech', 'programming'],
            blacklisted_users=['spam1', 'spam2'],
            is_active=True
        )
        db.session.add(config)
        db.session.commit()

        # Create some interaction logs
        today = datetime.now(UTC)
        logs = [
            InteractionLog(
                account_id=account.id,
                interaction_type='follow',
                target_username=f'user_{i}',
                status='success',
                created_at=today
            )
            for i in range(5)
        ]
        db.session.add_all(logs)
        db.session.commit()

        # Count today's successful follows
        follow_count = InteractionLog.query.filter(
            InteractionLog.account_id == account.id,
            InteractionLog.interaction_type == 'follow',
            InteractionLog.status == 'success',
            func.date(InteractionLog.created_at) == today.date()
        ).count()

        # Verify counts and limits
        assert follow_count == 5
        assert follow_count < config.daily_follow_limit
        assert config.daily_follow_limit == 20