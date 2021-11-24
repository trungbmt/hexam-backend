from flask import Flask
import pymongo
from config import Config
from flask_pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_manager
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, ping_timeout=2, ping_interval=10)
import socket_app

csrf = CSRFProtect(app)

mongodb_client = MongoClient("mongodb+srv://trungbmt:hncUKt3dhGya00ko@cluster0.nspaq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = mongodb_client.hexam


import routes
from auth import auth
app.register_blueprint(auth, url_prefix='/auth')


if __name__ == '__main__':
    app.run(debug=True) 
    db.users.ensure_index( [("username", pymongo.ASCENDING), ("email", pymongo.ASCENDING)], unique=True )