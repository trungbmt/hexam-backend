from flask import flash, render_template, url_for, redirect
from forms import RegistrationForm, LoginForm
from app import app


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

