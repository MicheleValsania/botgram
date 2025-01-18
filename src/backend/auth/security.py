"""
Security utilities for authentication system.
"""
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import current_app, jsonify, request
from flask_jwt_extended import decode_token, get_jwt
from ..models import db
from ..models.models import Account, BlacklistedToken, SecurityLog
from ..api.responses import APIResponse

# Constants for brute force protection
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

def check_if_token_is_blacklisted(jwt_payload):
    """Check if a token has been blacklisted."""
    jti = jwt_payload["jti"]
    token = BlacklistedToken.query.filter_by(jti=jti).first()
    return bool(token)

def blacklist_token(token_jti, token_type, user_id, expires):
    """Add a token to the blacklist."""
    blacklisted_token = BlacklistedToken(
        jti=token_jti,
        token_type=token_type,
        user_id=user_id,
        expires=expires
    )
    db.session.add(blacklisted_token)
    db.session.commit()

def clean_blacklisted_tokens():
    """Remove expired tokens from the blacklist."""
    now = datetime.now(timezone.utc)
    BlacklistedToken.query.filter(BlacklistedToken.expires < now).delete()
    db.session.commit()

def record_failed_login(account):
    """Record a failed login attempt."""
    now = datetime.now(timezone.utc)
    account.failed_login_attempts += 1
    account.last_failed_login = now
    
    if account.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        account.locked_until = now + LOCKOUT_DURATION
    
    db.session.commit()

def reset_failed_login_attempts(account):
    """Reset the failed login attempts counter."""
    account.failed_login_attempts = 0
    account.last_failed_login = None
    account.locked_until = None
    db.session.commit()

def check_brute_force_protection(account):
    """Check if the account is locked due to too many failed attempts."""
    if not account.locked_until:
        return True, None
    
    now = datetime.now(timezone.utc)
    locked_until = account.locked_until.replace(tzinfo=timezone.utc) if account.locked_until else None
    
    if locked_until and locked_until > now:
        time_remaining = (locked_until - now).total_seconds() / 60
        return False, f"Account is locked. Try again in {int(time_remaining)} minutes."
    
    # Reset if lock has expired
    reset_failed_login_attempts(account)
    return True, None

def require_not_blacklisted():
    """Decorator to check if a token is blacklisted."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            jwt_payload = get_jwt()
            if check_if_token_is_blacklisted(jwt_payload):
                return APIResponse.error(
                    message="Token has been revoked",
                    status_code=401
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def log_security_event(event_type, account_id=None, request=None, details=None):
    """Log a security event."""
    if request:
        ip_address = request.remote_addr
        user_agent = request.user_agent.string if request.user_agent else None
    else:
        ip_address = None
        user_agent = None
    
    log = SecurityLog(
        account_id=account_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details
    )
    
    db.session.add(log)
    db.session.commit()

def get_security_logs(account_id=None, event_type=None, start_date=None, end_date=None, limit=100):
    """Retrieve security logs with optional filtering."""
    query = SecurityLog.query
    
    if account_id:
        query = query.filter(SecurityLog.account_id == account_id)
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    if start_date:
        query = query.filter(SecurityLog.created_at >= start_date)
    if end_date:
        query = query.filter(SecurityLog.created_at <= end_date)
    
    return query.order_by(SecurityLog.created_at.desc()).limit(limit).all()
