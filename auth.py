from bcrypt import hashpw
from flask.helpers import flash, url_for
from flask.templating import render_template
from forms import LoginForm, RegistrationForm
from flask import Blueprint, json, redirect
from app import db
import utils


auth = Blueprint('auth', __name__)

@auth.route("/sign-up", methods=['GET', 'POST'])
def register():
    registerForm = RegistrationForm()
    
    if registerForm.validate_on_submit():
        # exist_email = db.users.find_one({"email": registerForm.email.data})
        exist_user = db.users.find_one({"$or":[ 
            {"email":registerForm.email.data}, 
            {"username":registerForm.username.data}
        ]})
        if exist_user:
            if(exist_user['email']==registerForm.email.data):
                flash("Địa chỉ email đã tồn tại!", "danger")
            else:
                flash("Tên đăng nhập đã tồn tại!", "danger")
        else:
            user = {
                "email": registerForm.email.data,
                "username": registerForm.username.data,
                "password": utils.get_hashed_password(registerForm.password.data)
            }
            if db.users.insert_one(user):
                flash("Đăng ký tài khoản thành công!", "success")
                return redirect('/home')
            else:
                flash("Lỗi hệ thống!")
    return render_template('auth/register.html', form=registerForm, title="Đăng ký")


@auth.route("/login", methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        exist_email = db.users.find_one({"email": loginForm.email.data})
        print(utils.get_hashed_password(loginForm.password.data))
        if exist_email:
            if utils.check_password(loginForm.password.data, exist_email['password']):
                flash("Đăng nhập thành công!", "success")
                return redirect('/home')
        flash("Tài khoản hoặc mật khẩu không chính xác!", "danger")
    return render_template('auth/login.html', form=loginForm)


@auth.route("/logout")
def logout():
    return "Logout"