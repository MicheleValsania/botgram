# Botgram Project Continuity Document

## Overview
Questo documento fornisce informazioni essenziali sul progetto Botgram, inclusi i componenti principali, le funzionalità implementate e le decisioni di design.

## Componenti Principali

### Rate Limiting
- **Implementazione**: Decoratore `auth_rate_limits` in `src/backend/middleware/rate_limit.py`
- **Funzionalità**:
  - Limite di 5 richieste per indirizzo IP
  - Tracciamento di tutte le richieste di autenticazione (successo e fallimento)
  - Reset automatico dopo 60 secondi
- **Dipendenze**:
  - Flask-Limiter per la gestione del rate limiting
  - Memorizzazione in memoria (`memory://`)

### Autenticazione
- **File**: `src/backend/middleware/auth.py`
- **Funzionalità**:
  - Registrazione utente con validazione password
  - Login con gestione token JWT
  - Protezione endpoint con decoratore
- **Endpoints**:
  - `/api/auth/register`
  - `/api/auth/login`

### Logging
- **File**: `src/backend/middleware/logging.py`
- **Caratteristiche**:
  - Logging strutturato per richieste e risposte
  - Tracciamento tempi di esecuzione
  - Mascheramento dati sensibili

## Test Suite

### Test di Rate Limiting
- **File**: `tests/integration/test_rate_limit.py`
- **Test Principali**:
  - `test_login_rate_limit`: Verifica limite login
  - `test_register_rate_limit`: Verifica limite registrazione
  - `test_rate_limit_reset`: Verifica reset timer
  - `test_different_endpoints_rate_limits`: Verifica limiti indipendenti

### Test di Stress
- **File**: `tests/integration/test_stress.py`
- **Test Principali**:
  - `test_auth_rate_limiting`: Test di carico autenticazione
  - `test_api_rate_limiting`: Test di carico API

## Configurazione

### Rate Limiter
```python
app.config['RATELIMIT_HEADERS_ENABLED'] = True
app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
app.config['RATELIMIT_KEY_PREFIX'] = 'botgram'
```

### Headers di Rate Limit
- `X-RateLimit-Retry-After`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Formato Risposte API

### Successo
```json
{
    "data": {},
    "success": true
}
```

### Errore
```json
{
    "error": "Messaggio di errore",
    "error_code": "CODICE_ERRORE",
    "success": false
}
```

## Decisioni di Design

### Rate Limiting
1. **Conteggio Richieste**: Tutte le richieste di autenticazione vengono conteggiate, incluse quelle fallite (401)
2. **Storage**: Utilizzo di storage in memoria per ambiente di sviluppo
3. **Reset Timer**: Timer di 60 secondi per il reset del contatore

### Autenticazione
1. **Token JWT**: Utilizzo di token JWT per la gestione delle sessioni
2. **Validazione Password**: Regole specifiche per la sicurezza delle password
3. **Protezione Endpoint**: Decoratore per proteggere gli endpoint sensibili

## Note per lo Sviluppo Futuro

### Miglioramenti Pianificati
1. **Storage Persistente**: Implementare storage Redis per il rate limiting in produzione
2. **Logging Avanzato**: Aggiungere logging su file per ambiente di produzione
3. **Metriche**: Implementare monitoraggio delle prestazioni e degli errori

### Problemi Noti
1. **Rate Limiting**: Il contatore potrebbe essere resettato se il server viene riavviato
2. **Test**: Alcuni test potrebbero essere sensibili al timing

## Comandi Utili

### Test
```bash
# Esegui tutti i test
pytest

# Esegui test specifici
pytest tests/integration/test_rate_limit.py -v
pytest tests/integration/test_stress.py -v
```

### Sviluppo
```bash
# Attiva ambiente virtuale
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Avvia server di sviluppo
flask run
```

## Contatti e Risorse
- **Repository**: [Botgram Repository](https://github.com/yourusername/botgram)
- **Documentazione API**: [API Documentation](docs/api.md)
- **Team**: [Team Contacts](docs/team.md)
