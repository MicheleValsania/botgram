"""
Schemi per la validazione dei dati Instagram.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError

class SessionSchema(Schema):
    """Schema per la creazione di una sessione Instagram."""
    username = fields.Str(required=True)
    session_id = fields.Str(required=True)
    cookies = fields.Dict(required=True)
    user_agent = fields.Str(required=True)

class BaseActionSchema(Schema):
    """Schema base per le azioni Instagram."""
    username = fields.Str(required=True)
    action_type = fields.Str(required=True, 
                           validate=validate.OneOf(['follow', 'like', 'comment']))

class FollowSchema(BaseActionSchema):
    """Schema per l'azione di follow."""
    target_user_id = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'follow')

class LikeSchema(BaseActionSchema):
    """Schema per l'azione di like."""
    media_id = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'like')

class CommentSchema(BaseActionSchema):
    """Schema per l'azione di commento."""
    media_id = fields.Str(required=True)
    comment_text = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'comment')

class UserInfoSchema(Schema):
    """Schema per le informazioni dell'utente Instagram."""
    username = fields.Str(required=True)
    full_name = fields.Str(allow_none=True)
    biography = fields.Str(allow_none=True)
    followers_count = fields.Int(allow_none=True)
    following_count = fields.Int(allow_none=True)
    is_private = fields.Bool(allow_none=True)
    is_verified = fields.Bool(allow_none=True)
    profile_pic_url = fields.Str(allow_none=True)

class PostSchema(Schema):
    """Schema per i post Instagram."""
    shortcode = fields.Str(required=True)
    caption = fields.Str(allow_none=True)
    like_count = fields.Int(allow_none=True)
    comment_count = fields.Int(allow_none=True)
    media_type = fields.Str(allow_none=True)
    taken_at = fields.DateTime(allow_none=True)
    location = fields.Dict(allow_none=True)

class RateLimitSchema(Schema):
    """Schema per le informazioni sui limiti di richieste."""
    follow_remaining = fields.Int(required=True)
    like_remaining = fields.Int(required=True)
    comment_remaining = fields.Int(required=True)
    reset_time = fields.DateTime(required=True)
