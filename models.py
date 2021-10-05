from bson.json_util import loads, dumps
from bson.objectid import ObjectId
from flask.json import jsonify
from app import db
from app import login_manager
from flask_login import UserMixin
import utils

class User(UserMixin):
    def __init__(self, _id, username, email, password, displayname=None, gender=None, phone=None, address=None, fb_id=None, gg_id=None, dob=None, avatar=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.displayname = displayname
        self.phone = phone
        self.fb_id = fb_id
        self.gg_id = gg_id
        self.dob = dob
        self.avatar = avatar
        self.address = address
        self.gender = gender
        
    def is_authenticated():
        return True
    def is_active():
        return True
    def is_anonymous():
        return False
    def get_id(self):
        return str(self._id)

    def update_to_mongo(self):
        return db.users.update_one({'_id': self._id}, {'$set': self.json()})
        

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
        return ({
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "displayname": self.displayname,
            "phone": self.phone,
            "fb_id": self.fb_id,
            "gg_id": self.gg_id,
            "dob": self.dob,
            "avatar": self.avatar,
            "address": self.address,
            "gender": self.gender
        })

