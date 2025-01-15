import pytest
import os
import sys
from flask import Flask
from src.backend import create_app
from src.backend.config.database import db
from src.backend.models.models import Account
from src.backend.middleware.auth import hash_password

def setup_test_environment():
    """Prepara l'ambiente di test"""
    app = create_app('testing')
    
    with app.app_context():
        # Ricrea il database
        db.drop_all()
        db.create_all()
        
        # Crea un account di test
        test_account = Account(
            username='test_user',
            email='test@example.com',
            password_hash=hash_password('Test123!')
        )
        db.session.add(test_account)
        db.session.commit()
        
        print("✅ Ambiente di test preparato")
        return test_account.id

def run_tests():
    """Esegue i test"""
    try:
        print("🚀 Avvio suite di test...")
        
        # Setup ambiente
        account_id = setup_test_environment()
        
        # Esegue i test
        print("\n🔄 Esecuzione test...")
        pytest.main(['-v', 
                    'tests/integration/test_stress.py',
                    'tests/integration/test_edge_cases.py'])
        
        print("\n✨ Tutti i test completati!")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione dei test: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Assicurati che il working directory sia corretto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.chdir(project_root)
    run_tests()