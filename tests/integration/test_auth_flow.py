"""
Integration tests for the authentication flow.
"""
import pytest
from datetime import datetime, timedelta, timezone
from flask import url_for
from flask_jwt_extended import decode_token
from src.backend.models import db
from src.backend.models.models import Account, BlacklistedToken, SecurityLog
from src.backend.auth.security import MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION

def test_successful_auth_flow(client, test_user):
    """Test the complete successful authentication flow."""
    # Step 1: Login
    login_response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    assert login_response.status_code == 200
    tokens = login_response.json['data']
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens
    
    # Verify security log was created
    log = SecurityLog.query.filter_by(
        account_id=test_user['id'],
        event_type='login_success'
    ).first()
    assert log is not None
    
    # Step 2: Access protected endpoint
    protected_response = client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert protected_response.status_code == 200
    
    # Step 3: Logout
    logout_response = client.post(
        '/api/auth/logout',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert logout_response.status_code == 200
    
    # Verify token was blacklisted
    blacklisted = BlacklistedToken.query.filter_by(
        user_id=test_user['id']
    ).first()
    assert blacklisted is not None
    
    # Verify security log was created for logout
    logout_log = SecurityLog.query.filter_by(
        account_id=test_user['id'],
        event_type='logout'
    ).first()
    assert logout_log is not None
    
    # Step 4: Verify token is now invalid
    protected_response = client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens["access_token"]}'}
    )
    assert protected_response.status_code == 401

def test_brute_force_protection(client, test_user):
    """Test brute force protection mechanism."""
    # Attempt multiple failed logins
    for _ in range(MAX_LOGIN_ATTEMPTS):
        response = client.post('/api/auth/login', json={
            'email': test_user['email'],
            'password': 'wrong_password'
        })
        assert response.status_code == 401
    
    # Verify account is now locked
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']  # Correct password
    })
    assert response.status_code == 429
    
    # Verify security logs were created
    failed_logs = SecurityLog.query.filter_by(
        account_id=test_user['id'],
        event_type='login_failed'
    ).all()
    assert len(failed_logs) == MAX_LOGIN_ATTEMPTS
    
    blocked_log = SecurityLog.query.filter_by(
        account_id=test_user['id'],
        event_type='login_blocked'
    ).first()
    assert blocked_log is not None
    
    # Fast forward time to after lockout period
    test_user_account = Account.query.get(test_user['id'])
    test_user_account.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.session.commit()
    
    # Verify login works after lockout period
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    assert response.status_code == 200

def test_token_refresh_flow(client, test_user):
    """Test the token refresh flow."""
    # Login to get tokens
    login_response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    tokens = login_response.json['data']
    
    # Use refresh token to get new access token
    refresh_response = client.post(
        '/api/auth/refresh',
        headers={'Authorization': f'Bearer {tokens["refresh_token"]}'}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json['data']
    assert 'access_token' in new_tokens
    
    # Verify new access token works
    protected_response = client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {new_tokens["access_token"]}'}
    )
    assert protected_response.status_code == 200

def test_concurrent_sessions(client, test_user):
    """Test handling of multiple active sessions."""
    # Login from two different "devices"
    login1 = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    login2 = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    
    tokens1 = login1.json['data']
    tokens2 = login2.json['data']
    
    # Both sessions should work
    assert client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens1["access_token"]}'}
    ).status_code == 200
    assert client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens2["access_token"]}'}
    ).status_code == 200
    
    # Logout from first session
    logout_response = client.post(
        '/api/auth/logout',
        headers={'Authorization': f'Bearer {tokens1["access_token"]}'}
    )
    assert logout_response.status_code == 200
    
    # First session should be invalid, second should still work
    assert client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens1["access_token"]}'}
    ).status_code == 401
    assert client.get(
        '/api/auth/me',
        headers={'Authorization': f'Bearer {tokens2["access_token"]}'}
    ).status_code == 200
