from bson.json_util import loads, dumps
import os, uuid
from bson.objectid import ObjectId
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

    login_user(user)

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
    list_request = Friend.get_request_by_receiver(current_user._id, 999)
    for i in list_request:
        i['sender'] = User.get_by_id(i['sender_id']).info()
    return dumps(list_request)

@app.route("/friends/<username>", methods=['POST'])
@login_required
def send_friend_request(username):
    #step 1: get user from username
    user = User.get_by_username(username)

    #step 2: prevent users from making friends with themselves
    if flask_login.current_user._id != user._id:

        #step 3: check if friendship available
        exits_frship = Friend.get_by_friendship(current_user._id, user._id)
        if exits_frship is not None:
            return Response(response="Không thể gửi lời mời kết bạn thêm nữa!", status=400)

        #step 4: create record with status = pending
        if Friend.make_request(current_user._id, user._id):
            return Response(response="Gửi lời mời kết bạn thành công!", status=200)
    return Response(response="Gửi lời mời kết bạn thất bại!", status=400)

@app.route("/respond-friends-request", methods=['POST'])
@login_required
def respond_friend_request():
    #Step 1: get request id & respond type from request
    request_id = request.form['request_id']
    respond_type = request.form['type'].lower()
    #Step 2: check if available request & current user is receiver of request & status of request is "pending"
    exits_request = Friend.get_by_id(request_id)
    if exits_request and current_user._id == exits_request.receiver_id and exits_request.status.lower() == "pending":
        #Step 3: if type= "accept" then change status of request from "pending" to "accepted" else remove request
        if respond_type == "accept":
            exits_request.status = "accepted"
            exits_request.update()
        elif respond_type == "deny":
            exits_request.remove()
        return Response(response="Thao tác thành công!", status=200)
    
    return Response(response="Không tồn tại yêu cầu kết bạn này!", status=400)

@app.route("/friends", methods=['GET'])
@login_required
def get_friend_list():

    list_friend = Friend.get_friend_by_id(current_user._id, 999)

    return dumps(list_friend)