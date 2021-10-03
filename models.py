from bson.objectid import ObjectId
from app import db
from app import login_manager
from flask_login import UserMixin
import utils

class User(UserMixin):
    def __init__(self, _id, username, email, password, phone=None, fb_id=None, gg_id=None, dob=None, avatar=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.fb_id = fb_id
        self.gg_id = gg_id
        self.dob = dob
        self.avatar = avatar
        
    def is_authenticated():
        return True
    def is_active():
        return True
    def is_anonymous():
        return False
    def get_id(self):
        return str(self._id)

    @classmethod
    def get_by_username(cls, username):
        data = db.users.find_one({"username": username})
        if data is not None:
            return cls(**data)
    @classmethod
    def get_by_email(cls, email):
        data = db.users.find_one({"email": email})
        if data is not None:
            return cls(**data)
    @classmethod
    def get_by_id(cls, _id):
        data = db.users.find_one({"_id": ObjectId(_id)})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return utils.check_password(password, verify_user.password)
        return False

    def json(self):
        return {
            "username": self.username,
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

