from bson.objectid import ObjectId
from app import db
from datetime import datetime


class Participants:
    def __init__(self, title, user_id, conversation_id, _id=None, join_by= None, seen=None):
        self.title = title
        self.user_id = user_id
        self.conversation_id = conversation_id
        self._id = _id
        self.join_by = join_by
        self.seen = seen
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.participants.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)

    @classmethod
    def seen_by_c_u(cls, conversation_id, user_id):
        db.participants.update_one(
            {"$and":[
                {"conversation_id": ObjectId(conversation_id)}, 
                {"user_id": ObjectId(user_id)}
            ]},
            {"$set": {
                "seen": True
            }}
        )
        return True

    @classmethod
    def seen_by_id(cls, _id, is_seen):
        db.participants.update_one(
            {"_id": ObjectId(_id)},
            {"$set": {
                "seen": is_seen
            }}
        )
        return True

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

    @classmethod
    def get_by_c_and_u(cls, conversation_id, user_id):
        data = db.participants.find_one({"$and": [
            {"conversation_id": ObjectId(conversation_id)},
            {"user_id": ObjectId(user_id)}
        ]})
        return data
    @classmethod
    def change_participant_name(cls, conversation_id, current_user_id, name):
        participant = cls(**cls.get_other_user_in_private(conversation_id, current_user_id))
        participant.title = name
        if participant.update():
            return True
        return False
    @classmethod
    def change_nickname(cls, conversation_id, user_id, nickname):
        data = db.participants.find_one({"$and": [
            {"conversation_id": ObjectId(conversation_id)},
            {"user_id": ObjectId(user_id)}
        ]})
        if data is not None:
            participant = cls(**data)
            participant.title = nickname
            participant.update()
            return participant
        return None

    def insert(self):
        return db.participants.insert_one(self.bson())

    def update(self):
        return db.participants.update_one({"_id": ObjectId(self._id)}, {"$set": self.bson()})
        
    def delete(self):
        return db.participants.delete_one({"_id": ObjectId(self._id)})

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
            "seen": self.seen
        }
    def json(self):
        return {
            "_id": str(self._id),
            "title": self.title,
            "user_id": str(self.user_id),
            "conversation_id": str(self.conversation_id),
            "join_by": self.join_by if self.join_by is not None else "",
            "seen": self.seen if self.seen is not None else "None"
        }