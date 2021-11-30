from operator import le
from bson.objectid import ObjectId
from pymongo import cursor
from app import db
from datetime import datetime

from local_models.participants import Participants


class Conversation:
    def __init__(self, title, type, avatar=None, _id=None, moderator_id= None, channel_id = None):
        self.title = title
        self.type = type
        self.moderator_id = moderator_id
        self._id = _id
        self.channel_id = channel_id
        self.avatar = avatar
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.conversation.find_one({"_id": ObjectId(_id)})
        if data is not None:
            return cls(**data)

    def has_user(self, user_id):
        has_user = db.participants.find_one({"conversation_id": self._id, "user_id": user_id})
        if has_user is not None:
            return True
        return False
    @classmethod
    def get_info_conversation(cls, conversation_id, current_user_id):
        conversation = cls.get_by_id(conversation_id)
        if conversation.type.lower() == "private":
            participants = Participants.get_by_conversation(conversation_id)
            participants.find_one({"user_id": {
                "$ne": ObjectId(current_user_id)
            }})
            
    @classmethod
    def get_private_conversation(cls, user1_id, user2_id):
        data = db.conversation.aggregate([
            {"$match": {
                "type": "private"
            }},
            {"$lookup": {
                "from": "participants",
                "as": "participants",
                "let": {"user1_id": user1_id, "user2_id": user2_id, "conversation_id": "$_id"},
                "pipeline": [
                    {"$match": {
                        "$and": [
                            {"$or": [
                                {"$expr": {"$eq": ["$user_id", ObjectId(user1_id)]}},
                                {"$expr": {"$eq": ["$user_id", ObjectId(user2_id)]}},
                            ]},
                            {"$expr": {"$eq": ["$conversation_id", "$$conversation_id"]}}
                        ]
                    }},
                    {"$lookup": {
                        "from": "users",
                        "localField": "user_id",
                        "foreignField": "_id",
                        "as": "user"
                    }},
                    {"$unwind": "$user"}
                ]
            }},
            {"$project": {
                "participants.user.password": 0,
            }},
            {"$match": {
                "participants": {"$size": 2}
            }},
        ])
        result = next(data, None)
        return result
    
    @classmethod
    def get_list_conversation(cls, user_id):
        data = db.messages.aggregate([
            {"$sort": {"_id": -1}},
            {"$group": 
                {
                    "_id": "$conversation_id",
                    "message_id": {"$first": "$_id"},
                    "sender_id": {"$first": "$sender_id"},
                    "message": {"$first": "$message"},
                    "message_type": {"$first": "$message_type"},
                    "conversation_id": {"$first": "$conversation_id"},
                }
            },
            {"$lookup": {
                "from": "participants",
                "as": "myParticipant",
                "let": {"conversation_id": "$conversation_id"},
                "pipeline": [
                    {"$match": {
                        "$and": [
                            {"$expr": {"$eq": ["$conversation_id", "$$conversation_id"]}},
                            {"$expr": {"$eq": ["$user_id", ObjectId(user_id)]}},
                        ]
                    }}
                ]
            }},
            {"$unwind":"$myParticipant"},
            {"$match": 
                {"myParticipant": {"$exists": "true"}}
            },
            {"$lookup":
                {
                    "from": "users",
                    "localField": "sender_id",
                    "foreignField": "_id",
                    "as": "sender"
                }
            },
            {"$lookup":
                {
                    "from": "conversation",
                    "localField": "conversation_id",
                    "foreignField": "_id",
                    "as": "conversation"
                }
            },
            {"$lookup":
                {
                    "from": "participants",
                    "as": "participants",
                    "let": {"conversation_id": "$conversation_id"},
                    "pipeline": [
                        {"$match": 
                            {"$expr": {"$eq": ["$conversation_id", "$$conversation_id"]}},
                        },
                        {"$lookup":
                            {
                                "from": "users",
                                "localField": "user_id",
                                "foreignField": "_id",
                                "as": "user"
                            }
                        },
                        {"$unwind":"$user"},
                    ]
                }
            },
            {"$lookup":
                {
                    "from": "participants",
                    "as": "participant",
                    "let": {"conversation_id": "$conversation_id", "sender_id": "$sender_id"},
                    "pipeline": [
                        {"$match": {
                            "$and": [
                                {"$expr": {"$eq": ["$conversation_id", "$$conversation_id"]}},
                                {"$expr": {"$ne": ["$user_id", ObjectId(user_id)]}},
                            ]
                        }},
                        {"$limit": 1},
                        {"$lookup":
                            {
                                "from": "users",
                                "localField": "user_id",
                                "foreignField": "_id",
                                "as": "user"
                            }
                        },
                        {"$unwind":"$user"},
                    ]
                }
            },
            {"$project": {
                "sender.password": 0,
            }},
            {"$sort": {"message_id": -1}},
            {"$unwind":"$sender"},
            {"$unwind":"$participant"},
            {"$unwind":"$conversation"},
        ])
        return list(data)
    
    def insert(self):
        return db.conversation.insert_one(self.bson())

    def update(self):
        return db.conversation.update_one({"_id": self._id}, {"$set": self.bson()})
    @classmethod
    def create_private(cls):
        
        data = {
            "title": "",
            "type": "private",
        }
        conversation = cls(**data)
        result = conversation.insert()
        conversation_id = result.inserted_id

        return conversation_id


    def bson(self):
        return {
            "_id": ObjectId(self._id),
            "title": self.title,
            "type": self.type,
            "avatar": self.avatar,
            "moderator_id": self.moderator_id,
            "channel_id": self.channel_id
        }
    