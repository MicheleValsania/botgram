from src.backend.models.models import Account, db
from src.backend.app import create_app
from src.backend.middleware.auth import hash_password
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create a test user if it doesn't exist
        if not Account.query.filter_by(username='test').first():
            test_user = Account(
                username='test',
                password_hash=hash_password('test123'),
                email='test@example.com',
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully!")
        else:
            print("Test user already exists!")

if __name__ == '__main__':
    init_db()
