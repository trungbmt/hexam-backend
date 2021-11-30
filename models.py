from datetime import datetime
from bson.json_util import loads, dumps
from bson.objectid import ObjectId
from flask import url_for
from flask.helpers import send_from_directory
from flask.json import jsonify
import pymongo
from app import db
from app import login_manager
from flask_login import UserMixin
import utils

class User(UserMixin):
    def __init__(self, _id, username, email, password, displayname=None, gender=None, phone=None, address=None, fb_id=None, gg_id=None, dob=None, avatar="images/default_avatar.png", created_at= datetime.now()):
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
        self.created_at = created_at
        
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

    def info(self):
        return ({
            "_id": str(self._id),
            "name": self.displayname or self.username,
            "username": self.username,
            "email": self.email,
            "displayname": self.displayname,
            "phone": self.phone,
            "fb_id": self.fb_id,
            "gg_id": self.gg_id,
            "dob": self.dob,
            "avatar": self.avatar,
            "address": self.address,
            "gender": int(self.gender) if self.gender else None
        })
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
            "gender": int(self.gender) if self.gender else None,
            "created_at": self.created_at
        })

class Friend():
    def __init__(self, sender_id, receiver_id, status, _id=None, created_at=datetime.now()):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.status = status
        self._id = _id
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, _id):
        data = db.friends.find_one({"_id": ObjectId(_id)})
        if data is not None:
            return cls(**data)

    def count_pending(_id):
        data = db.friends.find({"receiver_id": ObjectId(_id), "status": "pending"}).sort('created_at',pymongo.DESCENDING).count()
        return data
    def count_friend(_id):
        data = db.friends.find(
            {"$and":[ 
                {"$or":[ 
                    {"sender_id":ObjectId(_id)}, 
                    {"receiver_id":ObjectId(_id)}]}, 
                {"status": "accepted"}]}).sort('created_at',pymongo.DESCENDING).count()
        return data

    @classmethod
    def make_request(cls, sender_id, receiver_id):
        data = cls(sender_id, receiver_id, "pending")
        return db.friends.insert_one(data.bson())
    @classmethod
    def get_friend_by_id(cls, _id, limit=0, offset=0, skip=0, scopeName=""):
        data = db.friends.aggregate([
            {"$lookup": {
                "from": "users",
                "localField": "sender_id",
                "foreignField": "_id",
                "as": "sender"
            }},
            {"$lookup": {
                "from": "users",
                "localField": "receiver_id",
                "foreignField": "_id",
                "as": "receiver"
            }},
            {"$project": {
                "_id": 1,
                "sender_id": 1,
                "receiver_id": 1,
                "sender": 1,
                "receiver": 1,
                "status": 1,
                "friend_info": {
                    "$switch": {
                        "branches": [
                            { "case": { "$eq": [ "$sender_id", ObjectId(_id) ] }, "then": "$receiver" },
                            { "case": { "$eq": [ "$receiver_id", ObjectId(_id) ] }, "then": "$sender" }
                        ]
                    }
                }
            }},
            {"$match": {
                "$and": [
                    {"$or": [
                        {"friend_info.displayname": { '$regex': '.*'+scopeName+'.*', '$options': 'i'}},
                        {"friend_info.username": { '$regex': '.*'+scopeName+'.*', '$options': 'i'}},
                    ]},
                    {"status": "accepted"},
                    {"$or": [
                        {"sender_id": _id},
                        {"receiver_id": _id}
                    ]}
                ]
                
            }},
            {"$project": {
                "sender.password": 0,
                "receiver.password": 0
            }},
            {"$unwind":"$friend_info"},
        ])
        if data is not None:
            return list(data)

    @classmethod
    def get_request_by_receiver(cls, receiver_id, limit):
        data = db.friends.find({"receiver_id": ObjectId(receiver_id), "status": "pending"}).sort('created_at',pymongo.DESCENDING).limit(limit)
        if data is not None:
            return list(data)
    
    
    def get_by_friendship(receiver_id, sender_id):
        data = db.friends.find_one(
            {"$or":[ 
                {"$and":[ 
                    {"sender_id":ObjectId(sender_id)}, 
                    {"receiver_id":ObjectId(receiver_id)}]}, 
                {"$and":[ 
                    {"sender_id":ObjectId(receiver_id)}, 
                    {"receiver_id":ObjectId(sender_id)}]}
            ]})
        if data is not None:
            return Friend(**data)

    def friends_for_create_chat(user_id):
        pass

    
    def update(self):
        return db.friends.update_one({'_id': self._id}, {'$set': self.bson()})

    def remove(self):
        return db.friends.delete_one({'_id': self._id})

    def json(self):
        return ({
            "_id": str(self._id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "status": self.status,
            "created_at": str(self.created_at)
        })
    def bson(self):
        return {
            "sender_id": ObjectId(self.sender_id),
            "receiver_id": ObjectId(self.receiver_id),
            "status": str(self.status),
            "created_at": self.created_at
        }
