from flask import flash, render_template, url_for, redirect
from forms import RegistrationForm, LoginForm
from app import app


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    registerForm = RegistrationForm()
    
    if registerForm.validate_on_submit():
        flash(f'Tạo tài khoản {registerForm.username.data} thành công!', 'success')
        return redirect(url_for('home'))
    return render_template('auth/register.html', form=registerForm, title="Đăng ký")


@app.route("/login")
def login():
    loginForm = LoginForm()
    return render_template('templates/auth/login.html', form=loginForm)