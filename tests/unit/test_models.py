import pytest
from datetime import datetime
from src.backend.models.models import Account, Configuration, InteractionLog, TargetProfile
from src.backend.config.database import db

def test_account_creation(app, test_user):
    """Test Account model creation and basic attributes."""
    assert test_user.username == 'test_user'
    assert test_user.email == 'test@example.com'
    assert test_user.is_active is True
    assert isinstance(test_user.created_at, datetime)

def test_account_relationships(app, test_user, test_config):
    """Test Account model relationships."""
    # Test configuration relationship
    assert test_user.configurations is not None
    assert test_user.configurations.daily_like_limit == 50
    
    # Test interaction logs relationship
    log = InteractionLog(
        account_id=test_user.id,
        interaction_type='like',
        target_username='test_target',
        status='success'
    )
    db.session.add(log)
    db.session.commit()
    
    assert len(test_user.interaction_logs) == 1
    assert test_user.interaction_logs[0].interaction_type == 'like'

def test_configuration_creation(app, test_config):
    """Test Configuration model creation and validation."""
    assert test_config.daily_like_limit == 50
    assert test_config.daily_follow_limit == 20
    assert test_config.min_delay == 2.0
    assert test_config.max_delay == 5.0
    assert 'test' in test_config.target_hashtags
    assert 'blocked_user' in test_config.blacklisted_users

def test_configuration_account_relationship(app, test_user, test_config):
    """Test Configuration and Account bidirectional relationship."""
    assert test_config.account_id == test_user.id
    assert test_config.account == test_user
    assert test_user.configurations == test_config

def test_interaction_log_creation(app, test_user):
    """Test InteractionLog model creation and attributes."""
    log = InteractionLog(
        account_id=test_user.id,
        interaction_type='follow',
        target_username='test_target',
        status='success'
    )
    db.session.add(log)
    db.session.commit()

    assert log.interaction_type == 'follow'
    assert log.target_username == 'test_target'
    assert log.status == 'success'
    assert isinstance(log.created_at, datetime)
    assert log.account == test_user

def test_target_profile_creation(app, test_user):
    """Test TargetProfile model creation and attributes."""
    target = TargetProfile(
        account_id=test_user.id,
        username='target_user',
        followers_count=1000,
        following_count=500,
        engagement_rate=5.2,
        is_private=False,
        is_verified=False,
        status='pending'
    )
    db.session.add(target)
    db.session.commit()

    assert target.username == 'target_user'
    assert target.followers_count == 1000
    assert target.following_count == 500
    assert target.engagement_rate == 5.2
    assert target.is_private is False
    assert target.status == 'pending'
    assert target.account == test_user

def test_cascade_delete(app, test_user, test_config):
    """Test cascade delete functionality."""
    # Add some related records
    log = InteractionLog(
        account_id=test_user.id,
        interaction_type='like',
        target_username='test_target',
        status='success'
    )
    target = TargetProfile(
        account_id=test_user.id,
        username='target_user',
        status='pending'
    )
    db.session.add_all([log, target])
    db.session.commit()

    # Delete the user
    db.session.delete(test_user)
    db.session.commit()

    # Check if related records are deleted
    assert Configuration.query.filter_by(account_id=test_user.id).first() is None
    assert InteractionLog.query.filter_by(account_id=test_user.id).first() is None
    assert TargetProfile.query.filter_by(account_id=test_user.id).first() is None