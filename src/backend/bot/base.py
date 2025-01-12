from typing import Dict, List, Optional
import logging
import asyncio
import random
from datetime import datetime
from sqlalchemy import func
from .session import InstagramSession
from .interactions import LikeInteraction, FollowInteraction, UnfollowInteraction, HashtagInteraction
from ..models.models import Account, Configuration, InteractionLog, TargetProfile
from ..config.database import db

class InstagramBot:
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.config: Optional[Configuration] = None
        self.session: Optional[InstagramSession] = None
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.actions = {
            'like': LikeInteraction(self),
            'follow': FollowInteraction(self),
            'unfollow': UnfollowInteraction(self),
            'hashtag': HashtagInteraction(self)
        }
        self.current_delays = {
            'like': 0,
            'follow': 0,
            'unfollow': 0
        }

    async def initialize(self, instagram_password: str) -> bool:
        """Inizializza il bot caricando la configurazione"""
        try:
            # Carica l'account e la configurazione
            account = Account.query.get(self.account_id)
            if not account:
                self.logger.error(f"Account {self.account_id} non trovato")
                return False

            self.config = Configuration.query.filter_by(account_id=self.account_id).first()
            if not self.config:
                self.logger.error(f"Nessuna configurazione trovata per l'account {self.account_id}")
                return False

            if not self.config.is_active:
                self.logger.error(f"Configurazione non attiva per l'account {self.account_id}")
                return False

            # Inizializza la sessione Instagram
            self.session = InstagramSession(
                username=account.username,
                proxy_settings=self.config.proxy_settings
            )
            
            # Effettua il login
            if not await self.session.login(instagram_password):
                self.logger.error("Login Instagram fallito")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Errore durante l'inizializzazione del bot: {str(e)}")
            return False

    async def start(self) -> None:
        """Avvia il bot"""
        if self.running:
            self.logger.warning("Il bot è già in esecuzione")
            return

        if not self.session:
            self.logger.error("Sessione Instagram non inizializzata")
            return

        self.running = True
        try:
            while self.running:
                await self._execute_cycle()
                await self._respect_limits()
        except Exception as e:
            self.logger.error(f"Errore durante l'esecuzione del bot: {str(e)}")
        finally:
            self.running = False
            await self.stop()

    async def stop(self) -> None:
        """Ferma il bot"""
        self.running = False
        if self.session:
            await self.session.close()
            self.session = None

    async def _execute_cycle(self) -> None:
        """Esegue un ciclo di interazioni"""
        try:
            # Processa gli hashtag configurati
            if self.config.target_hashtags:
                hashtag = random.choice(self.config.target_hashtags)
                posts = await self.actions['hashtag'].execute(hashtag)
                
                for post in posts:
                    # Verifica se l'utente è in blacklist
                    if post['user']['username'] in (self.config.blacklisted_users or []):
                        continue
                    
                    # Possibile like al post
                    if await self._check_daily_limits('like'):
                        await self.actions['like'].execute(post['id'], post['user']['username'])
                    
                    # Possibile follow all'utente
                    if (random.random() < 0.3  # 30% di probabilità di follow
                            and await self._check_daily_limits('follow')):
                        await self.actions['follow'].execute(post['user']['username'])
                    
                    await self._respect_limits()
            
            # Gestione unfollow
            if await self._check_daily_limits('unfollow'):
                # Trova utenti da unfollow
                # TODO: Implementare logica per selezionare utenti da unfollow
                pass

        except Exception as e:
            self.logger.error(f"Errore durante il ciclo di esecuzione: {str(e)}")

    async def _respect_limits(self) -> None:
        """Gestisce i delay tra le azioni"""
        if not self.config:
            return

        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        await asyncio.sleep(delay)

    def _log_interaction(self, interaction_type: str, target_username: str, 
                        status: str, error_message: Optional[str] = None) -> None:
        """Registra un'interazione nel database"""
        try:
            log = InteractionLog(
                account_id=self.account_id,
                interaction_type=interaction_type,
                target_username=target_username,
                status=status,
                error_message=error_message,
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Errore durante il logging dell'interazione: {str(e)}")

    async def _check_daily_limits(self, interaction_type: str) -> bool:
        """Verifica se sono stati raggiunti i limiti giornalieri"""
        try:
            today = datetime.utcnow().date()
            count = InteractionLog.query.filter(
                InteractionLog.account_id == self.account_id,
                InteractionLog.interaction_type == interaction_type,
                InteractionLog.status == 'success',
                func.date(InteractionLog.created_at) == today
            ).count()

            limit_map = {
                'like': self.config.daily_like_limit,
                'follow': self.config.daily_follow_limit,
                'unfollow': self.config.daily_unfollow_limit
            }

            return count < limit_map.get(interaction_type, 0)

        except Exception as e:
            self.logger.error(f"Errore durante il controllo dei limiti: {str