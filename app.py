from forms import RegistrationForm
from flask import Flask
from flask.templating import render_template
import json
import pymongo
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

client = pymongo.MongoClient("mongodb+srv://trungbmt:hncUKt3dhGya00ko@cluster0.nspaq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client['hexam']


@app.route("/register")
def register():
    registerForm = RegistrationForm()
    return render_template('auth/register.html', form=registerForm, title="Đăng ký")

if __name__ == '__main__':
    app.run(debug=True)