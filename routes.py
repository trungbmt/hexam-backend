from flask import app
from flask.templating import render_template
from forms import RegistrationForm, LoginForm
from app import Flask


@app.route("/")
@app.route("/home")
def home():
    return render_template('templates/home.html')

@app.route("/register")
def register():
    registerForm = RegistrationForm()
    return render_template('templates/auth/register.html', form=registerForm)


@app.route("/login")
def login():
    loginForm = LoginForm()
    return render_template('templates/auth/login.html', form=loginForm)