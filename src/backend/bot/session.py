from typing import Optional, Dict
import logging
from instagrapi import Client
from fake_useragent import UserAgent
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta

class InstagramSession:
    def __init__(self, username: str, proxy_settings: Optional[Dict] = None):
        self.username = username
        self.proxy_settings = proxy_settings
        self.client: Optional[Client] = None
        self.logger = logging.getLogger(__name__)
        self.user_agent = UserAgent().random
        self.last_action = datetime.now()
        self._setup_client()

    def _setup_client(self) -> None:
        """Configura il client Instagram"""
        try:
            self.client = Client()
            
            # Configura proxy se specificato
            if self.proxy_settings:
                self.client.set_proxy(self.proxy_settings.get('url'))
            
            # Imposta user agent
            self.client.set_user_agent(self.user_agent)
            
            # Configura timeout e altri parametri
            self.client.set_timeout(10)
            self.client.delay_range = [1, 3]
            
        except Exception as e:
            self.logger.error(f"Errore durante il setup del client: {str(e)}")
            raise

    async def login(self, password: str) -> bool:
        """Effettua il login su Instagram"""
        try:
            # Verifica se esiste già una sessione salvata
            saved_session = await self._load_saved_session()
            if saved_session:
                self.client.load_settings(saved_session)
                self.logger.info("Sessione caricata dal salvataggio")
                return True

            # Altrimenti effettua un nuovo login
            login_success = self.client.login(self.username, password)
            if login_success:
                # Salva la sessione per usi futuri
                await self._save_session()
                self.logger.info("Login effettuato con successo")
                return True
            
            return False

        except Exception as e:
            self.logger.error(f"Errore durante il login: {str(e)}")
            return False

    async def _save_session(self) -> None:
        """Salva la sessione corrente"""
        try:
            session_data = self.client.get_settings()
            # TODO: Implementare il salvataggio sicuro della sessione (es. su Redis)
            
        except Exception as e:
            self.logger.error(f"Errore durante il salvataggio della sessione: {str(e)}")

    async def _load_saved_session(self) -> Optional[Dict]:
        """Carica una sessione salvata"""
        try:
            # TODO: Implementare il caricamento della sessione salvata
            return None
            
        except Exception as e:
            self.logger.error(f"Errore durante il caricamento della sessione: {str(e)}")
            return None

    def check_action_delay(self) -> float:
        """Calcola il delay necessario per la prossima azione"""
        time_since_last = (datetime.now() - self.last_action).total_seconds()
        if time_since_last < 1:
            return 1 - time_since_last
        return 0

    async def execute_action(self, action_type: str, *args, **kwargs):
        """Esegue un'azione Instagram con gestione dei delay"""
        delay = self.check_action_delay()
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            if action_type == 'like':
                result = await self.like_media(*args, **kwargs)
            elif action_type == 'follow':
                result = await self.follow_user(*args, **kwargs)
            elif action_type == 'unfollow':
                result = await self.unfollow_user(*args, **kwargs)
            elif action_type == 'get_hashtag_medias':
                result = await self.get_hashtag_medias(*args, **kwargs)
            else:
                raise ValueError(f"Tipo di azione non supportato: {action_type}")

            self.last_action = datetime.now()
            return result

        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione dell'azione {action_type}: {str(e)}")
            raise

    async def like_media(self, media_id: str) -> bool:
        """Mette like a un media"""
        try:
            return self.client.media_like(media_id)
        except Exception as e:
            self.logger.error(f"Errore durante il like del media {media_id}: {str(e)}")
            return False

    async def follow_user(self, user_id: str) -> bool:
        """Segue un utente"""
        try:
            return self.client.user_follow(user_id)
        except Exception as e:
            self.logger.error(f"Errore durante il follow dell'utente {user_id}: {str(e)}")
            return False

    async def unfollow_user(self, user_id: str) -> bool:
        """Smette di seguire un utente"""
        try:
            return self.client.user_unfollow(user_id)
        except Exception as e:
            self.logger.error(f"Errore durante l'unfollow dell'utente {user_id}: {str(e)}")
            return False

    async def get_hashtag_medias(self, hashtag: str, amount: int = 20) -> list:
        """Ottiene i media recenti per un hashtag"""
        try:
            return self.client.hashtag_medias_recent(hashtag, amount)
        except Exception as e:
            self.logger.error(f"Errore durante la ricerca hashtag {hashtag}: {str(e)}")
            return []

    async def close(self) -> None:
        """Chiude la sessione"""
        try:
            if self.client:
                self.client.logout()
            self.client = None
        except Exception as e:
            self.logger.error(f"Errore durante la chiusura della sessione: {str(e)}")