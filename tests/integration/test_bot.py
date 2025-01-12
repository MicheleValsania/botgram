import pytest
import asyncio
from datetime import datetime
from src.backend.bot.base import InstagramBot
from src.backend.models.models import InteractionLog, TargetProfile

@pytest.mark.asyncio
async def test_bot_initialization(app, test_user, test_config, mock_instagram_session):
    """Test bot initialization and configuration loading."""
    bot = InstagramBot(test_user.id)
    success = await bot.initialize("test_password")
    
    assert success is True
    assert bot.config is not None
    assert bot.config.daily_like_limit == test_config.daily_like_limit
    assert bot.session is not None
    assert isinstance(bot.session, mock_instagram_session)

@pytest.mark.asyncio
async def test_bot_session_management(app, test_user, test_config, mock_instagram_session):
    """Test bot session management."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")
    
    assert bot.session.logged_in is True
    
    await bot.stop()
    assert bot.running is False
    assert bot.session.logged_in is False

@pytest.mark.asyncio
async def test_interaction_limits(app, test_user, test_config, mock_instagram_session):
    """Test bot respects interaction limits."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")
    
    # Test like limits
    for _ in range(test_config.daily_like_limit):
        can_like = await bot._check_daily_limits('like')
        assert can_like is True
        await bot.actions['like'].execute('test_media_id', 'test_user')
    
    can_like = await bot._check_daily_limits('like')
    assert can_like is False

@pytest.mark.asyncio
async def test_interaction_logging(app, test_user, test_config, mock_instagram_session):
    """Test interaction logging functionality."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")
    
    # Execute some interactions
    await bot.actions['like'].execute('test_media_id', 'test_user')
    await bot.actions['follow'].execute('test_user')
    
    # Verify logs
    with app.app_context():
        logs = InteractionLog.query.filter_by(account_id=test_user.id).all()
        assert len(logs) == 2
        
        like_log = next(log for log in logs if log.interaction_type == 'like')
        assert like_log.target_media_id == 'test_media_id'
        assert like_log.status == 'success'

@pytest.mark.asyncio
async def test_delay_between_actions(app, test_user, test_config, mock_instagram_session):
    """Test bot respects delay between actions."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")
    
    start_time = datetime.now()
    
    # Execute multiple actions
    await bot.actions['like'].execute('media1', 'user1')
    await bot.actions['like'].execute('media2', 'user2')
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Verify minimum delay was respected
    assert duration >= test_config.min_delay

@pytest.mark.asyncio
async def test_target_handling(app, test_user, test_config, mock_instagram_session):
    """Test bot's target profile handling."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")
    
    # Test target hashtag processing
    hashtag = test_config.target_hashtags[0]
    posts = await bot.actions['hashtag'].execute(hashtag)
    assert len(posts) > 0
    
    # Verify target profiles are created
    with app.app_context():
        targets = TargetProfile.query.filter_by(account_id=test_user.id).all()
        assert len(targets) > 0
        
        first_target = targets[0]
        assert first_target.status == 'pending'
        assert first_target.username is not None

@pytest.mark.asyncio
async def test_error_handling(app, test_user, test_config, mock_instagram_session):
    """Test bot's error handling capabilities."""
    bot = InstagramBot(test_user.id)
    await bot.initialize("test_password")