from bson.objectid import ObjectId
from app import db


class Messages():
    def __init__(self, sender_id, conversation_id, message, _id=None, message_type=None, seen_by=None, created_at=None, deleted_at=None):
        self.sender_id = sender_id
        self.conversation_id = conversation_id
        self.message = message
        self._id = _id
        self.message_type = message_type
        self.seen_by = seen_by
        self.created_at = created_at
        self.deleted_at = deleted_at
        
    @classmethod
    def get_by_id(cls, _id):
        data = db.messages.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)

    def get_by_conversation(conversation_id):
        data = db.messages.find({"conversation_id": conversation_id})
        if data is not None:
            return list(data)
