from bson.objectid import ObjectId
from app import db


class Paticipants:
    def __init__(self, title, user_id, conversation_id, _id=None, join_by= None, created_at = None):
        self.title = title
        self.user_id = user_id
        self.conversation_id = conversation_id
        self._id = _id
        self.join_by = join_by
        self.created_at = created_at
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.messages.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)
    