"""
Modulo centralizzato per la gestione delle password.
Fornisce funzioni per l'hashing, la verifica e la validazione delle password.
"""

import re
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """
    Genera l'hash della password usando l'algoritmo più sicuro disponibile.
    
    Args:
        password: La password in chiaro
        
    Returns:
        str: L'hash della password
    """
    return generate_password_hash(password, method='pbkdf2:sha256:260000')

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica se una password corrisponde al suo hash.
    
    Args:
        password: La password in chiaro da verificare
        password_hash: L'hash della password con cui confrontare
        
    Returns:
        bool: True se la password corrisponde all'hash, False altrimenti
    """
    return check_password_hash(password_hash, password)

def validate_password(password: str) -> tuple[bool, str]:
    """
    Valida la password secondo criteri di sicurezza.
    
    Criteri:
    - Lunghezza minima: 8 caratteri
    - Almeno una lettera maiuscola
    - Almeno una lettera minuscola
    - Almeno un numero
    - Almeno un carattere speciale
    
    Args:
        password: La password da validare
        
    Returns:
        tuple[bool, str]: (True, "Password valida") se la password è valida,
                         (False, "Messaggio di errore") se non è valida
    """
    if len(password) < 8:
        return False, "La password deve essere lunga almeno 8 caratteri"
    
    if not re.search(r"[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola"
    
    if not re.search(r"[a-z]", password):
        return False, "La password deve contenere almeno una lettera minuscola"
    
    if not re.search(r"\d", password):
        return False, "La password deve contenere almeno un numero"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La password deve contenere almeno un carattere speciale"
    
    return True, "Password valida"
