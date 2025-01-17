from src.backend.models.models import Account, db
from src.backend.app import create_app
from src.backend.middleware.auth import hash_password
from datetime import datetime

def create_test_user():
    app = create_app()
    with app.app_context():
        # Delete existing test user if exists
        test_user = Account.query.filter_by(username='test').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
            print("Deleted existing test user")
        
        # Create new test user with valid password
        test_user = Account(
            username='test',
            password_hash=hash_password('TestUser123'),  # Rispetta tutti i criteri
            email='test@example.com',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
        print("Username: test")
        print("Password: TestUser123")

if __name__ == '__main__':
    create_test_user()
