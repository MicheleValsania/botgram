from datetime import UTC, datetime
from flask_login import UserMixin
from . import db

class Account(UserMixin, db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    configurations = db.relationship("Configuration", back_populates="account", uselist=False)
    interaction_logs = db.relationship("InteractionLog", back_populates="account")
    target_profiles = db.relationship("TargetProfile", back_populates="account")

class Configuration(db.Model):
    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), unique=True)
    daily_like_limit = db.Column(db.Integer, default=50)
    daily_follow_limit = db.Column(db.Integer, default=20)
    daily_unfollow_limit = db.Column(db.Integer, default=10)
    min_delay = db.Column(db.Float, default=2.0)  # In seconds
    max_delay = db.Column(db.Float, default=5.0)  # In seconds
    target_hashtags = db.Column(db.JSON)  # Store as JSON array
    blacklisted_users = db.Column(db.JSON)  # Store as JSON array
    proxy_settings = db.Column(db.JSON, nullable=True)  # Store proxy configuration as JSON
    user_agent = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(UTC), 
                           onupdate=lambda: datetime.now(UTC))
    # Relationship
    account = db.relationship("Account", back_populates="configurations")

class InteractionLog(db.Model):
    __tablename__ = 'interaction_logs'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    interaction_type = db.Column(db.String(50), nullable=False)  # 'like', 'follow', 'unfollow'
    target_username = db.Column(db.String(100))
    target_media_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50))  # 'success', 'failed'
    error_message = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # Relationship
    account = db.relationship("Account", back_populates="interaction_logs")

class TargetProfile(db.Model):
    __tablename__ = 'target_profiles'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    username = db.Column(db.String(100), nullable=False)
    followers_count = db.Column(db.Integer, nullable=True)
    following_count = db.Column(db.Integer, nullable=True)
    engagement_rate = db.Column(db.Float, nullable=True)
    last_post_date = db.Column(db.DateTime, nullable=True)
    is_private = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'processed', 'blacklisted'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), 
                         onupdate=lambda: datetime.now(UTC))
    # Relationship
    account = db.relationship("Account", back_populates="target_profiles")

# Create indexes
db.Index('ix_interaction_logs_created_at', InteractionLog.created_at)
db.Index('ix_target_profiles_username', TargetProfile.username)