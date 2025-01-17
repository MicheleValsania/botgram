"""Instagram API schemas."""
from marshmallow import Schema, fields

class SessionSchema(Schema):
    """Schema for session creation request."""
    username = fields.Str(required=True)
    session_id = fields.Str(required=True)
    cookies = fields.Dict(required=True)
    user_agent = fields.Str(required=True)

class FollowSchema(Schema):
    """Schema for follow user request."""
    username = fields.Str(required=True)
    target_user_id = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'follow')

class LikeSchema(Schema):
    """Schema for like post request."""
    username = fields.Str(required=True)
    media_id = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'like')

class CommentSchema(Schema):
    """Schema for comment post request."""
    username = fields.Str(required=True)
    media_id = fields.Str(required=True)
    comment_text = fields.Str(required=True)
    action_type = fields.Str(required=True, validate=lambda x: x == 'comment')
