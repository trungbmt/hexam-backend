from forms import RegistrationForm, LoginForm
from app import render_template
from app import app


@app.route("/")
@app.route("/home")
def home():
    return render_template('templates/home.html')

@app.route("/register")
def register():
    registerForm = RegistrationForm()
    return render_template('auth/register.html', form=registerForm, title="Đăng ký")


@app.route("/login")
def login():
    loginForm = LoginForm()
    return render_template('templates/auth/login.html', form=loginForm)