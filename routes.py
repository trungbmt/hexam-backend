from flask import flash, render_template, url_for, redirect, request
import flask_login
from app import app
from forms import UpdateAccountForm
from models import User

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Trang chủ")

@app.route("/profile/<username>", methods=['GET', 'POST'])
def profile(username):
    if request.method == 'POST':
        form = UpdateAccountForm()
        pass
    else:
        user = User.get_by_username(username)
        # if flask_login.current_user.is_authenticated:
        if user:
            return render_template('profile/show.html', 
                title = username + " Profile",
                user = user
            )
        else:
            return redirect('/404')

