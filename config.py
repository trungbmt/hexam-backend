import secrets

class Config(object):
    SECRET_KEY = secrets.token_urlsafe(16)