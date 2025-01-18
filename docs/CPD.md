# Detailed Development Plan

## Obiettivo
Implementare un sistema di autenticazione funzionale e sicuro per supportare lo sviluppo del core e del frontend.

## 1. Fix Importazioni e Dipendenze (Completed)
- [x] Updated [middleware/__init__.py](../src/backend/middleware/__init__.py) per rimuovere importazioni duplicate
- [x] Updated [backend/__init__.py](../src/backend/__init__.py) per includere JWTManager
- [x] Aggiornare `conftest.py` per utilizzare i nuovi percorsi dei moduli
- [x] Verificare le importazioni circolari

## 2. Core Autenticazione (In Progress)
- [x] Implementare e testare:
  - [x] Login/Logout
  - [x] Registrazione
  - [x] Protezione delle route
  - [x] Gestione token JWT
- [x] Aggiungere validazione base degli input
- [x] Implementare gestione errori

## 3. Testing Essenziale (In Progress)
- [x] Test unitari per:
  - [x] Autenticazione base (login/logout)
  - [x] Registrazione
  - [x] Validazione token
- [ ] Test di integrazione per i flussi principali

## 4. Documentazione Base
- [x] Aggiornare docstrings delle funzioni principali
- [x] Documentare gli endpoint di autenticazione
- [ ] Aggiungere esempi di utilizzo base

## 5. Miglioramenti e Ottimizzazioni (In Progress)
- [x] Migliorare la gestione degli errori
  - [x] Implementare eccezioni personalizzate
  - [x] Aggiungere messaggi di errore descrittivi
  - [x] Standardizzare il formato delle risposte di errore
- [x] Ottimizzare il rate limiting
  - [x] Aggiungere supporto per ambiente di test
  - [x] Implementare limiti specifici per endpoint
- [ ] Migliorare la sicurezza
  - [ ] Implementare blacklist token
  - [ ] Aggiungere protezione contro attacchi brute force
  - [ ] Implementare logging di sicurezza

## Quick Start
### Backend
```bash
# Attiva l'ambiente virtuale
source venv/bin/activate

# Installa le dipendenze se non già fatto
pip install -r requirements.txt

# Avvia il backend (dalla cartella src/backend)
cd src/backend
flask run --port 5000
# oppure con hot reload
FLASK_APP=__init__.py FLASK_ENV=development flask run --port 5000
```

### Frontend
```bash
# Installa le dipendenze se non già fatto
cd src/frontend
npm install

# Avvia il frontend in modalità sviluppo
npm run dev
# Il frontend sarà disponibile su http://localhost:5173
```

### Accesso
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Swagger/API Docs: http://localhost:5000/api/docs

## Dependencies
```
flask==3.0.0
flask-jwt-extended==4.7.1
flask-login==0.6.3
marshmallow==3.25.1
pytest==7.4.4
flask-limiter==3.5.0
```

## Note
- Feature aggiuntive come 2FA, password reset, email validation ecc. verranno implementate in una fase successiva, dopo aver completato le funzionalità core dell'applicazione.
- Il sistema di autenticazione è stato testato e funziona correttamente per i casi d'uso base.
- È stata implementata una gestione degli errori robusta con messaggi descrittivi.
- Il rate limiting è configurato per proteggere gli endpoint di autenticazione da abusi.
