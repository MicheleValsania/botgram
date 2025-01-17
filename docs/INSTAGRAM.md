# Instagram Integration Documentation

## Overview
The Instagram integration provides a robust system for managing Instagram sessions and performing automated actions while respecting Instagram's rate limits and terms of service.

## Components

### 1. Session Management
The session management system handles Instagram user sessions, including creation, validation, and expiration.

#### InstagramSession
- Manages individual user sessions
- Tracks rate limits for different actions
- Handles session expiration
- Validates session state

```python
session = InstagramSession.create(
    username="user123",
    session_id="session_xyz",
    cookies={"sessionid": "abc123"},
    user_agent="Mozilla/5.0..."
)
```

#### InstagramSessionManager
- Singleton manager for all Instagram sessions
- Handles session creation and retrieval
- Manages session cleanup
- Ensures thread safety

```python
# Create a new session
session = InstagramSessionManager.create_session(...)

# Get existing session
session = InstagramSessionManager.get_session("username")

# Invalidate session
InstagramSessionManager.invalidate_session("username")
```

### 2. Instagram Client
The Instagram client handles all interactions with Instagram's web API.

#### Features
- Follow users
- Like posts
- Comment on posts
- Session validation
- Rate limit enforcement
- Error handling

```python
client = InstagramClient(username="user123")
response, status = client.follow_user("target_user")
response, status = client.like_post("media_id")
response, status = client.comment_post("media_id", "Great post!")
```

### 3. API Endpoints

#### Session Management
```http
POST /api/instagram/session
DELETE /api/instagram/session/{username}
GET /api/instagram/limits/{username}
```

#### Actions
```http
POST /api/instagram/follow
POST /api/instagram/like
POST /api/instagram/comment
```

### 4. Rate Limiting

#### Default Limits
- Follow: 200 per day
- Like: 1000 per day
- Comment: 100 per day

#### Implementation
- Per-user tracking
- Rolling window
- Automatic reset
- Configurable limits

## Configuration

### Instagram Config
```python
class InstagramConfig:
    BASE_URL = "https://www.instagram.com/api/v1"
    FOLLOW_LIMIT_PER_DAY = 200
    LIKE_LIMIT_PER_DAY = 1000
    COMMENT_LIMIT_PER_DAY = 100
    SESSION_EXPIRY_HOURS = 24
```

## Error Handling

### Error Types
- `INVALID_SESSION`: Session not found or expired
- `RATE_LIMIT_EXCEEDED`: Action limit reached
- `REQUEST_FAILED`: Instagram API request failed
- `VALIDATION_ERROR`: Invalid input data

### Response Format
```json
{
    "success": false,
    "error_code": "ERROR_CODE",
    "message": "Error description",
    "errors": {}  // Validation errors if applicable
}
```

## Testing

### Unit Tests
- Session management tests
- Instagram client tests
- Rate limiting tests
- Error handling tests

### Integration Tests
- API endpoint tests
- End-to-end workflow tests
- Rate limit integration tests
- Error scenarios tests

## Security Considerations

### Session Security
- Secure cookie handling
- Session expiration
- Rate limit enforcement
- Input validation

### API Security
- Token-based authentication
- Request validation
- Error masking
- Rate limiting

## Best Practices

### Rate Limiting
1. Always check remaining limits before actions
2. Implement exponential backoff
3. Respect Instagram's terms of service
4. Monitor rate limit usage

### Session Management
1. Regular session cleanup
2. Proper error handling
3. Secure storage of credentials
4. Session validation before actions

### Error Handling
1. Proper error classification
2. Detailed error messages
3. Secure error responses
4. Logging for debugging

## Example Usage

### Creating a Session
```python
# Create new session
response = requests.post("/api/instagram/session", json={
    "username": "user123",
    "session_id": "xyz789",
    "cookies": {"sessionid": "abc123"},
    "user_agent": "Mozilla/5.0..."
})
```

### Performing Actions
```python
# Follow a user
response = requests.post("/api/instagram/follow", json={
    "username": "user123",
    "target_user_id": "target456",
    "action_type": "follow"
})

# Like a post
response = requests.post("/api/instagram/like", json={
    "username": "user123",
    "media_id": "post789",
    "action_type": "like"
})
```

### Checking Limits
```python
# Get remaining limits
response = requests.get("/api/instagram/limits/user123")
limits = response.json()["data"]["limits"]
```

## Monitoring and Maintenance

### Monitoring
- Rate limit usage
- Session states
- Error rates
- API response times

### Maintenance Tasks
- Regular session cleanup
- Rate limit resets
- Error log analysis
- Performance optimization

## Future Improvements

### Planned Features
1. Advanced rate limiting strategies
2. Bulk action support
3. Analytics dashboard
4. Enhanced error reporting

### Optimization Opportunities
1. Session storage optimization
2. Rate limit calculation efficiency
3. Request batching
4. Response caching
