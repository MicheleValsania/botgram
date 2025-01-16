# Botgram Project Continuity Document

## Overview
This document provides essential information about the Botgram project, including main components, implemented features, and design decisions.

## Main Components

### Rate Limiting
- **Implementation**: `auth_rate_limits` decorator in `src/backend/middleware/rate_limit.py`
- **Features**:
  - 5 requests limit per IP address
  - Tracking of all authentication requests (success and failure)
  - Automatic reset after 60 seconds
- **Dependencies**:
  - Flask-Limiter for rate limiting management
  - In-memory storage (`memory://`)

### Authentication
- **File**: `src/backend/middleware/auth.py`
- **Features**:
  - User registration with password validation
  - Login with JWT token management
  - Endpoint protection with decorator
- **Endpoints**:
  - `/api/auth/register`
  - `/api/auth/login`

### Logging
- **File**: `src/backend/middleware/logging.py`
- **Features**:
  - Structured logging for requests and responses
  - Execution time tracking
  - Sensitive data masking

## Test Suite

### Rate Limiting Tests
- **File**: `tests/integration/test_rate_limit.py`
- **Main Tests**:
  - `test_login_rate_limit`: Verifies login limit
  - `test_register_rate_limit`: Verifies registration limit
  - `test_rate_limit_reset`: Verifies timer reset
  - `test_different_endpoints_rate_limits`: Verifies independent limits

### Stress Tests
- **File**: `tests/integration/test_stress.py`
- **Main Tests**:
  - `test_auth_rate_limiting`: Authentication load testing
  - `test_api_rate_limiting`: API load testing

## Configuration

### Rate Limiter
```python
app.config['RATELIMIT_HEADERS_ENABLED'] = True
app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
app.config['RATELIMIT_KEY_PREFIX'] = 'botgram'
```

### Rate Limit Headers
- `X-RateLimit-Retry-After`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## API Response Format

### Success
```json
{
    "data": {},
    "success": true
}
```

### Error
```json
{
    "error": "Error message",
    "error_code": "ERROR_CODE",
    "success": false
}
```

## Design Decisions

### Rate Limiting
1. **Request Counting**: All authentication requests are counted, including failed ones (401)
2. **Storage**: In-memory storage used for development environment
3. **Reset Timer**: 60-second timer for counter reset

### Authentication
1. **JWT Token**: JWT tokens used for session management
2. **Password Validation**: Specific rules for password security
3. **Endpoint Protection**: Decorator to protect sensitive endpoints

## Future Development Notes

### Planned Improvements
1. **Persistent Storage**: Implement Redis storage for rate limiting in production
2. **Advanced Logging**: Add file logging for production environment
3. **Metrics**: Implement performance and error monitoring

### Known Issues
1. **Rate Limiting**: Counter might reset if server restarts
2. **Tests**: Some tests might be timing-sensitive

## Useful Commands

### Testing
```bash
# Run all tests
pytest

# Run specific tests
pytest tests/integration/test_rate_limit.py -v
pytest tests/integration/test_stress.py -v
```

### Development
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
flask run
```

## Contacts and Resources
- **Repository**: [Botgram Repository](https://github.com/yourusername/botgram)
- **API Documentation**: [API Documentation](docs/api.md)
- **Team**: [Team Contacts](docs/team.md)

## Code Examples

### Rate Limiting Decorator
```python
@auth_rate_limits()
def login():
    # Login logic here
    pass
```

### Authentication Middleware
```python
@jwt_required()
def protected_endpoint():
    # Protected endpoint logic here
    pass
```

### API Response Helper
```python
def api_response(data=None, success=True, status_code=200):
    response = {
        'data': data,
        'success': success
    }
    return jsonify(response), status_code
```

## System Architecture

### Components
1. **Web Server**: Flask application server
2. **Authentication**: JWT-based authentication system
3. **Rate Limiting**: In-memory rate limiting with Flask-Limiter
4. **Logging**: Structured logging system with sensitive data masking

### Data Flow
1. Request arrives at web server
2. Rate limiting check
3. Authentication verification (if required)
4. Business logic processing
5. Response formatting and sending

## Security Considerations

### Authentication
- JWT tokens with appropriate expiration
- Secure password validation rules
- Rate limiting on authentication endpoints

### Data Protection
- Sensitive data masking in logs
- Request validation
- Input sanitization

## Deployment

### Requirements
- Python 3.12+
- Flask and dependencies
- Virtual environment

### Environment Variables
```bash
FLASK_ENV=development
FLASK_APP=src/backend/app.py
JWT_SECRET_KEY=your-secret-key
```

### Production Considerations
1. Use production-grade WSGI server
2. Implement Redis for rate limiting
3. Configure proper logging
4. Set up monitoring and alerts

## Maintenance

### Regular Tasks
1. Monitor rate limiting effectiveness
2. Review logs for security issues
3. Update dependencies
4. Run test suite

### Backup Procedures
1. Regular database backups
2. Configuration backup
3. Log rotation and archival
