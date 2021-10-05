import os, uuid
from flask import flash, render_template, url_for, redirect, request, jsonify
from flask_login import current_user
from flask_login.utils import login_user
from app import app
from forms import UpdateAccountForm
from models import User
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Trang chủ")

@app.route("/profile/<username>", methods=['GET', 'POST'])
def profile(username):

    user = User.get_by_username(username)
    if not user:
        return redirect('/404')
    # login_user(user)
    form = UpdateAccountForm()
    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_authenticated:
            if(user.username == current_user.username):
                user.displayname = form.displayname.data
                user.phone = form.phone.data
                user.dob = form.dob.data
                user.gender = form.gender.data
                user.address = form.address.data

                if not user.email:
                    user.email = form.email.data

                file = form.picture.data
                if file and file.filename !='' and allowed_file(file.filename):
                    filename = str(uuid.uuid4().hex)+secure_filename(file.filename)
                    file.save(os.path.join(app.config['AVATAR_FOLDER'], filename))
                    user.avatar = 'images/avatars/'+filename

                

                user.update_to_mongo()
                
                flash("Cập nhật thành công!", "success")
                
    # if flask_login.current_user.is_authenticated:

    return render_template('profile/show.html', 
        title = username + " Profile",
        user = user,
        form = form
    )

