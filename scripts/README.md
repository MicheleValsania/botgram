# Botgram Utility Scripts

This directory contains utility scripts for managing the Botgram application.

## Database Scripts

### `init_db.py`
Initializes the database and creates the required tables.

Usage:
```bash
python scripts/init_db.py
```

### `create_test_user.py`
Creates a test user for development purposes. The user will have the following credentials:
- Username: `test`
- Password: `TestUser123`
- Email: `test@example.com`

The password follows all security requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

Usage:
```bash
python scripts/create_test_user.py
```

## Development Guidelines

When creating new utility scripts:
1. Place them in this directory
2. Add appropriate documentation in this README
3. Include error handling
4. Add logging where appropriate
5. Follow the existing code style
