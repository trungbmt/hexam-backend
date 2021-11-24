from datetime import datetime
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from app import db

class Attachment():
    def __init__(self, message_id, file_extention, file_path, file_name, _id=None):
        self.message_id = message_id
        self.file_extention = file_extention
        self.file_path = file_path
        self.file_name = file_name
        self._id = _id
    
    @classmethod
    def get_by_id(cls, _id):
        data = db.attachment.find_one({"_id", ObjectId(_id)})
        if data is not None:
            return cls(**data)
    @classmethod
    def get_by_message(cls, message_id):
        data = db.attachment.find_one({"message_id", ObjectId(message_id)})
        if data is not None:
            return cls(**data)

    def insert(self):
        return db.attachment.insert_one(self.bson())

    def bson(self):
        return {
            "_id": ObjectId(self._id),
            "message_id": ObjectId(self.message_id),
            "file_extention": self.file_extention,
            "file_path": self.file_path,
            "file_name": self.file_name
        }