from bson.json_util import loads, dumps
import os, uuid
from flask import flash, json, render_template, url_for, redirect, request, jsonify
from flask.helpers import send_from_directory
from flask.wrappers import Response
from flask_login import current_user
import flask_login
from flask_login.utils import login_required, login_user
from app import app
from forms import UpdateAccountForm
from models import Friend, User
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

    frship = None
    pending = 0
    if current_user.is_authenticated:
        frship = Friend.get_by_friendship(current_user._id, user._id)
        if current_user.username == user.username:
            pending = Friend.count_pending(current_user._id)


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
                
    return render_template('profile/show.html', 
        title = username + " Profile",
        user = user,
        form = form,
        frship = frship,
        pending = pending
    )
@app.route("/friends/pending")
@login_required
def get_friend_request():
    list_request = Friend.get_by_receiver(current_user._id, 10)
    for i in list_request:
        i['sender'] = User.get_by_id(i['sender_id']).info()
    return dumps(list_request)

@app.route("/friends/<username>", methods=['POST'])
@login_required
def send_friend_request(username):

    user = User.get_by_username(username)
    if flask_login.current_user._id != user._id:
        exits_frship = Friend.get_by_friendship(current_user._id, user._id)
        if exits_frship is not None:
            return Response(response="Không thể gửi lời mời kết bạn thêm nữa!", status=400)

        if Friend.make_request(current_user._id, user._id):
            return Response(response="Gửi lời mời kết bạn thành công!", status=200)
    return Response(response="Gửi lời mời kết bạn thất bại!", status=400)


        