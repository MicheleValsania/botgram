# Instagram Bot API Documentation

## Overview
This document describes the API endpoints available in the Instagram Bot Manager. All endpoints require authentication via Bearer token.

## Authentication
All requests must include an `Authorization` header with a valid Bearer token:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Session Management

#### Create Session
```http
POST /api/instagram/session
```

Creates a new Instagram session.

**Request Body:**
```json
{
    "username": "string",
    "session_id": "string",
    "cookies": {
        "sessionid": "string",
        "csrftoken": "string"
    },
    "user_agent": "string"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "session_created": true,
        "username": "string"
    }
}
```

#### End Session
```http
DELETE /api/instagram/session/{username}
```

Ends an Instagram session.

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "ok"
    }
}
```

### Instagram Operations

#### Follow User
```http
POST /api/instagram/follow
```

Follows a user on Instagram.

**Request Body:**
```json
{
    "username": "string",
    "target_user_id": "string",
    "action_type": "follow"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "ok"
    }
}
```

#### Like Post
```http
POST /api/instagram/like
```

Likes a post on Instagram.

**Request Body:**
```json
{
    "username": "string",
    "media_id": "string",
    "action_type": "like"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "ok"
    }
}
```

#### Comment on Post
```http
POST /api/instagram/comment
```

Comments on a post.

**Request Body:**
```json
{
    "username": "string",
    "media_id": "string",
    "comment_text": "string",
    "action_type": "comment"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "ok"
    }
}
```

### Rate Limits

#### Get User Limits
```http
GET /api/instagram/limits/{username}
```

Gets the current rate limits for a user.

**Response:**
```json
{
    "success": true,
    "data": {
        "username": "string",
        "limits": {
            "follow": "integer",
            "like": "integer",
            "comment": "integer"
        }
    }
}
```

## Error Responses

All endpoints may return the following error responses:

### Invalid Session
```json
{
    "success": false,
    "error": "Invalid session",
    "error_code": "INVALID_SESSION",
    "status_code": 401
}
```

### Rate Limit Exceeded
```json
{
    "success": false,
    "error": "Rate limit exceeded",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "status_code": 429
}
```

### Request Failed
```json
{
    "success": false,
    "error": "Network error",
    "error_code": "REQUEST_FAILED",
    "status_code": 500
}
```
