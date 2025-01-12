from marshmallow import Schema, fields, validate, ValidationError

class AccountSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    password = fields.Str(required=True, load_only=True)  # solo per il caricamento, mai per il dump
    email = fields.Email(required=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

class ConfigurationSchema(Schema):
    id = fields.Int(dump_only=True)
    account_id = fields.Int(dump_only=True)
    daily_like_limit = fields.Int(validate=validate.Range(min=0, max=1000))
    daily_follow_limit = fields.Int(validate=validate.Range(min=0, max=1000))
    daily_unfollow_limit = fields.Int(validate=validate.Range(min=0, max=1000))
    min_delay = fields.Float(validate=validate.Range(min=1.0))
    max_delay = fields.Float(validate=validate.Range(min=1.0))
    target_hashtags = fields.List(fields.Str())
    blacklisted_users = fields.List(fields.Str())
    proxy_settings = fields.Dict(allow_none=True)
    user_agent = fields.Str(allow_none=True)
    is_active = fields.Bool()

class InteractionLogSchema(Schema):
    id = fields.Int(dump_only=True)
    account_id = fields.Int(dump_only=True)
    interaction_type = fields.Str(validate=validate.OneOf(['like', 'follow', 'unfollow']))
    target_username = fields.Str()
    target_media_id = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(['success', 'failed']))
    error_message = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class TargetProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    account_id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    followers_count = fields.Int(allow_none=True)
    following_count = fields.Int(allow_none=True)
    engagement_rate = fields.Float(allow_none=True)
    last_post_date = fields.DateTime(allow_none=True)
    is_private = fields.Bool()
    is_verified = fields.Bool()
    status = fields.Str(validate=validate.OneOf(['pending', 'processed', 'blacklisted']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# Schemi per le risposte
class LoginResponseSchema(Schema):
    access_token = fields.Str()
    token_type = fields.Str()
    expires_in = fields.Int()
    user_id = fields.Int()

# Schema per il login
class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
