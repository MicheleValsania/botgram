from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    configurations = relationship("Configuration", back_populates="account", uselist=False)
    interaction_logs = relationship("InteractionLog", back_populates="account")
    target_profiles = relationship("TargetProfile", back_populates="account")

class Configuration(Base):
    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), unique=True)
    daily_like_limit = Column(Integer, default=50)
    daily_follow_limit = Column(Integer, default=20)
    daily_unfollow_limit = Column(Integer, default=10)
    min_delay = Column(Float, default=2.0)  # In seconds
    max_delay = Column(Float, default=5.0)  # In seconds
    target_hashtags = Column(JSON)  # Store as JSON array
    blacklisted_users = Column(JSON)  # Store as JSON array
    proxy_settings = Column(JSON, nullable=True)  # Store proxy configuration as JSON
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    account = relationship("Account", back_populates="configurations")

class InteractionLog(Base):
    __tablename__ = 'interaction_logs'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    interaction_type = Column(String(50), nullable=False)  # 'like', 'follow', 'unfollow'
    target_username = Column(String(100))
    target_media_id = Column(String(255), nullable=True)
    status = Column(String(50))  # 'success', 'failed'
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    account = relationship("Account", back_populates="interaction_logs")

class TargetProfile(Base):
    __tablename__ = 'target_profiles'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    username = Column(String(100), nullable=False)
    followers_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    last_post_date = Column(DateTime, nullable=True)
    is_private = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    status = Column(String(50), default='pending')  # 'pending', 'processed', 'blacklisted'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    account = relationship("Account", back_populates="target_profiles")

# Create indexes if needed
from sqlalchemy import Index

Index('ix_interaction_logs_created_at', InteractionLog.created_at)
Index('ix_target_profiles_username', TargetProfile.username)