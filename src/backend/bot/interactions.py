from typing import Dict, List, Optional
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from ..models.models import InteractionLog
from ..config.database import db

class BaseInteraction(ABC):
    """Base class for all Instagram interactions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    def log_interaction(self, target_username: str, status: str, 
                       error_message: Optional[str] = None,
                       media_id: Optional[str] = None) -> None:
        """Log the interaction in the database"""
        try:
            log = InteractionLog(
                account_id=self.bot.account_id,
                interaction_type=self.get_type(),
                target_username=target_username,
                target_media_id=media_id,
                status=status,
                error_message=error_message,
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error logging interaction: {str(e)}")

    @abstractmethod
    def get_type(self) -> str:
        """Return the type of interaction"""
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute the interaction"""
        pass

class LikeInteraction(BaseInteraction):
    """Handle liking posts"""
    
    def get_type(self) -> str:
        return 'like'

    async def execute(self, media_id: str, username: str) -> bool:
        """Like a specific post"""
        try:
            if not await self.bot._check_daily_limits('like'):
                self.logger.warning("Daily like limit reached")
                return False

            success = await self.bot.session.like_media(media_id)
            
            status = 'success' if success else 'failed'
            self.log_interaction(
                target_username=username,
                status=status,
                media_id=media_id
            )
            
            return success
        except Exception as e:
            self.logger.error(f"Error during like interaction: {str(e)}")
            self.log_interaction(
                target_username=username,
                status='failed',
                error_message=str(e),
                media_id=media_id
            )
            return False

class FollowInteraction(BaseInteraction):
    """Handle following users"""
    
    def get_type(self) -> str:
        return 'follow'

    async def execute(self, username: str) -> bool:
        """Follow a specific user"""
        try:
            if not await self.bot._check_daily_limits('follow'):
                self.logger.warning("Daily follow limit reached")
                return False

            success = await self.bot.session.follow_user(username)
            
            status = 'success' if success else 'failed'
            self.log_interaction(
                target_username=username,
                status=status
            )
            
            return success
        except Exception as e:
            self.logger.error(f"Error during follow interaction: {str(e)}")
            self.log_interaction(
                target_username=username,
                status='failed',
                error_message=str(e)
            )
            return False

class UnfollowInteraction(BaseInteraction):
    """Handle unfollowing users"""
    
    def get_type(self) -> str:
        return 'unfollow'

    async def execute(self, username: str) -> bool:
        """Unfollow a specific user"""
        try:
            if not await self.bot._check_daily_limits('unfollow'):
                self.logger.warning("Daily unfollow limit reached")
                return False

            success = await self.bot.session.unfollow_user(username)
            
            status = 'success' if success else 'failed'
            self.log_interaction(
                target_username=username,
                status=status
            )
            
            return success
        except Exception as e:
            self.logger.error(f"Error during unfollow interaction: {str(e)}")
            self.log_interaction(
                target_username=username,
                status='failed',
                error_message=str(e)
            )
            return False

class HashtagInteraction(BaseInteraction):
    """Handle hashtag-related operations"""
    
    def get_type(self) -> str:
        return 'hashtag'

    async def execute(self, hashtag: str, amount: int = 20) -> List[Dict]:
        """Get recent media for a hashtag"""
        try:
            medias = await self.bot.session.get_hashtag_medias(hashtag, amount)
            return medias
        except Exception as e:
            self.logger.error(f"Error during hashtag interaction: {str(e)}")
            return []