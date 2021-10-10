from bson.objectid import ObjectId
from app import db


class Conversation:
    def __init__(self, title, type, _id=None, moderator_id= None, channel_id = None, created_at = None):
        self.title = title
        self.type = type
        self.moderator_id = moderator_id
        self._id = _id
        self.channel_id = channel_id
        self.created_at = created_at
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.conversation.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)
    
    @classmethod
    def get_list_conversation(cls, user_id):
        data = db.messages.aggregate([
            {"$sort": {"created_at": -1}},
            {"$group": 
                {
                    "_id": "$conversation_id",
                    "sender_id": {"$first": "$sender_id"},
                    "message": {"$first": "$message"},
                    "message_type": {"$first": "$message_type"},
                    "created_at": {"$first": "$created_at"},
                    "conversation_id": {"$first": "$conversation_id"},
                }
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
                                {"$expr": {"$eq": ["$user_id", "$$sender_id"]}},
                            ]
                        }}
                    ]
                }
            },
            {"$sort": {"created_at": -1}},
            {"$unwind":"$sender"},
            {"$unwind":"$conversation"},
            {"$unwind":"$participant"}
        ])
        return list(data)

        data = db.participants.aggregate([
            {"$match":
                {
                    "user_id": ObjectId(user_id)
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
                    "from": "messages",
                    "let": {"conversation_id":"conversation_id"},
                    "as": "messages",
                    "pipeline": [
                        {"$sort": {
                            "created_at": -1
                        }},
                        {"$limit": 1},
                    ]
                }
            }
        ])
        if data is not None:
            return list(data)
    