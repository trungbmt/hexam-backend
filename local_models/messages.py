from datetime import datetime
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from app import db


class Messages():
    def __init__(self, sender_id, conversation_id, message, _id=None, message_type=None, seen_by=None, deleted_at=None):
        self.sender_id = sender_id
        self.conversation_id = conversation_id
        self.message = message
        self._id = _id
        self.message_type = message_type
        self.seen_by = seen_by
        self.deleted_at = deleted_at
        
    @classmethod
    def get_by_id(cls, _id):
        data = db.messages.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)

    def get_list_message(conversation_id, page=0):
        data = db.messages.aggregate([
            {"$sort": {"_id": -1}},
            {"$lookup": {
                "from": "users",
                "localField": "sender_id",
                "foreignField": "_id",
                "as": "sender"
            }},
            {"$lookup": {
                "from": "conversation",
                "localField": "conversation_id",
                "foreignField": "_id",
                "as": "conversation"
            }},
            {"$lookup": {
                "from": "attachment",
                "localField": "_id",
                "foreignField": "message_id",
                "as": "attachment"
            }},
            {"$lookup": {
                "from": "participants",
                "localField": "conversation_id",
                "foreignField": "conversation_id",
                "as": "participants"
            }},
            {"$match": {
                "conversation_id": ObjectId(conversation_id)
            }},
            {"$project": {
                "sender.password": 0
            }},
            {"$unwind":"$sender"},
            {"$unwind":"$conversation"},
            {"$unwind":
                {
                    "path": "$attachment",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {"$skip": page*20},
            {"$limit": 20},
        ])
        if data is not None:
            return list(data)
    
    def insert(self):
        return db.messages.insert_one(self.bson())

    def get_message_and_sender(_id):
        message_inserted = db.messages.aggregate([
            {"$match": 
                {'_id': _id}
            },
            {"$lookup": {
                
                "from": "users",
                "localField": "sender_id",
                "foreignField": "_id",
                "as": "sender"
            }},
            {"$lookup": {
                "from": "attachment",
                "localField": "_id",
                "foreignField": "message_id",
                "as": "attachment"
            }},
            {"$lookup": {
                "from": "conversation",
                "localField": "conversation_id",
                "foreignField": "_id",
                "as": "conversation"
            }},
            {"$unwind":"$sender"},
            {"$unwind":"$conversation"},
            {"$unwind":
                {
                    "path": "$attachment",
                    "preserveNullAndEmptyArrays": True
                }
            },
        ]).next()
        
        return message_inserted
    
    def bson(self):
        return {
            "_id": ObjectId(self._id),
            "sender_id": ObjectId(self.sender_id),
            "conversation_id": ObjectId(self.conversation_id),
            "message": self.message,
            "message_type": self.message_type,
            "seen_by": self.seen_by,
            "deleted_at": self.deleted_at
        }
    def json(self):
        return {
            "_id": str(self._id),
            "sender_id": str(self.sender_id),
            "conversation_id": str(self.conversation_id),
            "message": self.message,
            "message_type": self.message_type,
            "seen_by": self.seen_by,
            "deleted_at": self.deleted_at
        }


