from flask import Flask
import json
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://trungbmt:hncUKt3dhGya00ko@cluster0.nspaq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client['hexam']


@app.route('/')
def hello():
    print(db.user.find_one())
    return "Hello world test 123"

if __name__ == '__main__':
    app.run(debug=True)