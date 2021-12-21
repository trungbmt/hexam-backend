from flask.helpers import flash, url_for
from flask.scaffold import F
from flask.templating import render_template
from flask_login import LoginManager
import flask_login
from flask_login.utils import login_required, login_user, logout_user
from forms import LoginForm, RegistrationForm
from flask import Blueprint, redirect
from app import db
from app import app
import utils
from flask import request
from models import User



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user =User.get_by_id(user_id)
    if user is not None:
        return user
    else:
        return None
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'), code=302)

auth = Blueprint('auth', __name__)

@auth.route("/sign-up", methods=['GET', 'POST'])
def register():
    if flask_login.current_user.is_authenticated:
        return redirect('/home')

    registerForm = RegistrationForm()
    
    if registerForm.validate_on_submit():
        # exist_email = db.users.find_one({"email": registerForm.email.data})
        exist_user = db.users.find_one({"$or":[ 
            {"email":registerForm.email.data}, 
            {"username":registerForm.username.data}
        ]})
        if exist_user:
            if(exist_user['email']==registerForm.email.data):
                flash("Địa chỉ email đã tồn tại!", "error")
            else:
                flash("Tên đăng nhập đã tồn tại!", "error")
        else:
            user = {
                "email": registerForm.email.data,
                "username": registerForm.username.data,
                "displayname": registerForm.username.data,
                "avatar": "images/default_avatar.png",
                "password": utils.get_hashed_password(registerForm.password.data)
            }
            if db.users.insert_one(user):
                loguser = User.get_by_email(user['email'])
                login_user(loguser)
                flash("Đăng ký tài khoản thành công!", "success")
                return redirect('/home')
            else:
                flash("Lỗi hệ thống!", "error")
    return render_template('auth/register.html', form=registerForm, title="Đăng ký")


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect('/home')

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        if User.login_valid(loginForm.email.data, loginForm.password.data):
            user = User.get_by_email(loginForm.email.data)
            login_user(user, remember=loginForm.remember.data)
            flash("Chào {}, đăng nhập thành công!".format(user.username), "success")
            return redirect('/home')
        flash("Tài khoản hoặc mật khẩu không chính xác!", "error")
    return render_template('auth/login.html', form=loginForm)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/auth/login')