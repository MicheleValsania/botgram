import pytest
import jwt
from datetime import datetime, timedelta
from src.backend.middleware.auth import (
    generate_token,
    validate_password,
    hash_password,
    verify_password
)

def test_password_validation():
    """Test password validation rules."""
    # Test valid passwords
    valid_passwords = [
        "TestPass123",
        "SecureP@ssw0rd",
        "MyP@ssw0rd123"
    ]
    for password in valid_passwords:
        is_valid, message = validate_password(password)
        assert is_valid is True, f"Password should be valid: {password}, got message: {message}"

    # Test invalid passwords
    invalid_cases = [
        ("short", "length"),
        ("withoutdigits", "number"),
        ("lowercase123", "uppercase"),
        ("UPPERCASE123", "lowercase"),
        ("Ab1", "length")
    ]
    for password, expected_error in invalid_cases:
        is_valid, message = validate_password(password)
        assert is_valid is False
        assert expected_error.lower() in message.lower()

def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPass123"
    
    # Test hash generation
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0
    
    # Test verification
    assert verify_password(hashed, password) is True
    assert verify_password(hashed, "WrongPass123") is False
    
    # Test different hashes for same password
    another_hash = hash_password(password)
    assert hashed != another_hash  # Should use different salts
    assert verify_password(another_hash, password) is True

def test_token_generation(app, test_user):
    """Test JWT token generation and validation."""
    # Generate token
    token = generate_token(test_user.id)
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify token
    secret_key = app.config['SECRET_KEY']
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    
    assert payload['sub'] == test_user.id
    assert 'exp' in payload
    assert 'iat' in payload
    
    # Verify expiration
    exp_time = datetime.fromtimestamp(payload['exp'])
    iat_time = datetime.fromtimestamp(payload['iat'])
    assert exp_time > datetime.utcnow()
    assert exp_time - iat_time == timedelta(days=1)  # Token should expire in 1 day

def test_token_expiration(app):
    """Test token expiration handling."""
    # Create an expired token
    payload = {
        'exp': datetime.utcnow() - timedelta(days=1),
        'iat': datetime.utcnow() - timedelta(days=2),
        'sub': 1
    }
    expired_token = jwt.encode(
        payload,
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    # Verify it raises ExpiredSignatureError
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, app.config['SECRET_KEY'], algorithms=['HS256'])

def test_invalid_token(app):
    """Test invalid token handling."""
    # Test with invalid signature
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': 1
    }
    token = jwt.encode(payload, 'wrong_secret', algorithm='HS256')
    
    # Verify it raises InvalidTokenError
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

def test_token_payload_structure(app, test_user):
    """Test token payload structure and content."""
    token = generate_token(test_user.id)
    payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    
    # Check required fields
    required_fields = ['sub', 'exp', 'iat']
    for field in required_fields:
        assert field in payload
    
    # Check field types
    assert isinstance(payload['sub'], int)
    assert isinstance(payload['exp'], int)
    assert isinstance(payload['iat'], int)
    
    # Check logical constraints
    assert payload['iat'] < payload['exp']
    assert payload['sub'] == test_user.id