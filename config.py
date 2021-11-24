import secrets

class Config(object):
    SECRET_KEY = secrets.token_urlsafe(16)
    AVATAR_FOLDER = 'static/images/avatars'
    FILE_FOLDER = 'static/files'
    ping_interval = 5