from bson.objectid import ObjectId
from app import db
from datetime import datetime


class Participants:
    def __init__(self, title, user_id, conversation_id, _id=None, join_by= None):
        self.title = title
        self.user_id = user_id
        self.conversation_id = conversation_id
        self._id = _id
        self.join_by = join_by
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.messages.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)
    

    def get_by_conversation(conversation_id):

        data = db.participants.find({"conversation_id": ObjectId(conversation_id)})
        if data is not None:
            return list(data)
    
    def get_by_conversation_with_user(conversation_id):

        data = db.participants.aggregate([
            {"$match": {
                "conversation_id": ObjectId(conversation_id)
            }},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }},
            {"$unwind": "$user"}
        ])
        if data is not None:
            return list(data)
        
    @classmethod
    def get_other_user_in_private(cls, conversation_id, current_user_id):
        data = db.participants.find_one({"$and": [
            {"conversation_id": ObjectId(conversation_id)},
            {"user_id": {
                "$ne": ObjectId(current_user_id)
            }}
        ]})
        return data

    def insert(self):
        return db.participants.insert_one(self.bson())

    @classmethod
    def create_participant(cls, conversation_id, user, join_by):
        data = {
            "title": user.displayname,
            "user_id": user._id,
            "conversation_id": conversation_id,
            "join_by": join_by
        }
        participant = cls(**data)
        result = participant.insert()

        return result.inserted_id
    
    def bson(self):
        return {
            "_id": ObjectId(self._id),
            "title": self.title,
            "user_id": ObjectId(self.user_id),
            "conversation_id": ObjectId(self.conversation_id),
            "join_by": self.join_by,
        }