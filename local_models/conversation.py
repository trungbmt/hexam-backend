from bson.objectid import ObjectId
from app import db
from datetime import datetime


class Conversation:
    def __init__(self, title, type, _id=None, moderator_id= None, channel_id = None):
        self.title = title
        self.type = type
        self.moderator_id = moderator_id
        self._id = _id
        self.channel_id = channel_id
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.conversation.find_one({"_id": ObjectId(_id)})
        if data is not None:
            return cls(**data)

    def has_user(self, user_id):
        has_user = db.participants.find_one({"conversation_id": self._id, "user_id": user_id})
        print(has_user)
        if has_user is not None:
            return True
        return False

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
    