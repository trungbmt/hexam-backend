from flask import Flask
from config import Config
from flask_pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)


mongodb_client = MongoClient("mongodb+srv://trungbmt:hncUKt3dhGya00ko@cluster0.nspaq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = mongodb_client.hexam

import routes
from auth import auth
app.register_blueprint(auth, url_prefix='/auth')


if __name__ == '__main__':
    app.run(debug=True) 