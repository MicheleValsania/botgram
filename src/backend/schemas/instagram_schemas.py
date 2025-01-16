"""
Schemas for Instagram-related data validation.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError

class InstagramActionSchema(Schema):
    """Base schema for Instagram actions."""
    username = fields.Str(required=True)
    action_type = fields.Str(required=True, 
                           validate=validate.OneOf(['follow', 'like', 'comment']))

class InstagramFollowSchema(InstagramActionSchema):
    """Schema for follow action."""
    target_user_id = fields.Str(required=True)

class InstagramLikeSchema(InstagramActionSchema):
    """Schema for like action."""
    media_id = fields.Str(required=True)

class InstagramCommentSchema(InstagramActionSchema):
    """Schema for comment action."""
    media_id = fields.Str(required=True)
    comment_text = fields.Str(required=True, 
                            validate=validate.Length(min=1, max=2200))
    
    @validates('comment_text')
    def validate_comment(self, value):
        """Validates comment text for Instagram rules."""
        if len(value.split()) > 100:
            raise ValidationError("Comment cannot exceed 100 words")

class InstagramSessionSchema(Schema):
    """Schema for Instagram session data."""
    username = fields.Str(required=True)
    session_id = fields.Str(required=True)
    cookies = fields.Dict(required=True)
    user_agent = fields.Str(required=True)

class InstagramUserInfoSchema(Schema):
    """Schema for Instagram user information."""
    username = fields.Str(required=True)
    full_name = fields.Str(allow_none=True)
    biography = fields.Str(allow_none=True)
    followers_count = fields.Int(allow_none=True)
    following_count = fields.Int(allow_none=True)
    is_private = fields.Bool(allow_none=True)
    is_verified = fields.Bool(allow_none=True)
    profile_pic_url = fields.Str(allow_none=True)

class InstagramPostSchema(Schema):
    """Schema for Instagram post data."""
    shortcode = fields.Str(required=True)
    caption = fields.Str(allow_none=True)
    like_count = fields.Int(allow_none=True)
    comment_count = fields.Int(allow_none=True)
    media_type = fields.Str(allow_none=True)
    taken_at = fields.DateTime(allow_none=True)
    location = fields.Dict(allow_none=True)

class InstagramRateLimitSchema(Schema):
    """Schema for rate limit information."""
    follow_remaining = fields.Int(required=True)
    like_remaining = fields.Int(required=True)
    comment_remaining = fields.Int(required=True)
    reset_time = fields.DateTime(required=True)
