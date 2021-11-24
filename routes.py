from bson import json_util
from bson.json_util import loads, dumps
import os, uuid
from bson.objectid import ObjectId
from flask import flash, json, render_template, url_for, redirect, request, jsonify
from flask.helpers import send_from_directory
from flask.wrappers import Response
from flask_login import current_user
import flask_login
from flask_login.utils import login_required, login_user
from app import app, db
from forms import UpdateAccountForm
from local_models.attachment import Attachment
from models import Friend, User
from werkzeug.utils import secure_filename

from local_models.conversation import Conversation
from local_models.messages import Messages
from local_models.participants import Participants
from socket_app import sendMessageTo

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@app.route("/home")
def home():
    login_user(User.get_by_username("phamductrungbmt"))
    return render_template('home.html', title="Trang chủ")

@app.route("/phamductrungbmt")
def login_trung():
    login_user(User.get_by_username("phamductrungbmt"))
    return redirect('messages')

@app.route("/trungbmtvippro")
def trungbmtvippro():
    login_user(User.get_by_username("trungbmtvippro"))
    return redirect('/messages')

@app.route("/tqnguyen")
def login_nguyen():
    login_user(User.get_by_username("tqnguyen"))
    return redirect('/messages')

@app.route("/triemqn")
def login_triem():
    login_user(User.get_by_username("triemqn"))
    return redirect('/messages')

@app.route("/messages")
def messages():
    list_conversation = Conversation.get_list_conversation(current_user._id)
    return render_template('home.html', 
        title="Trang chủ", 
        list_conversation=list_conversation
    )


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

@app.route("/get_messages/<id_conversation>", methods=['POST'])
@login_required
def get_messages(id_conversation):
    conversation = Conversation.get_by_id(id_conversation)

    if conversation and conversation.has_user(current_user._id):
        list_message = Messages.get_list_message(id_conversation)
        return dumps(list_message)
    return "Bạn không có quyền truy cập vào cuộc trò truyện này!", 401

@app.route("/send_message/<id_conversation>", methods=['POST'])
@login_required
def send_message(id_conversation):
    conversation = Conversation.get_by_id(id_conversation)

    if conversation and conversation.has_user(current_user._id):
        data = {
            "sender_id": current_user._id,
            "conversation_id": conversation._id,
            "message": request.form['message'],
            "message_type": request.form['type'] if 'type' in request.form else "message",
        }
        message = Messages(**data)
        result = message.insert()
        if result is not None:
            message_inserted = Messages.get_message_and_sender(result.inserted_id)
            json_mess = json.loads(json_util.dumps(message_inserted))


            participants = Participants.get_by_conversation_with_user(id_conversation)
            
            if conversation.type.lower() == "private":
                json_mess['participants'] = json.loads(json_util.dumps(participants))

            for participant in participants:
                sendMessageTo(participant['user_id'], json_mess)
            return "success", 200
    return "failed", 400
@app.route("/send_file/<id_conversation>", methods=['POST'])
@login_required
def send_file(id_conversation):
    conversation = Conversation.get_by_id(id_conversation)
    if conversation and conversation.has_user(current_user._id):
        file = request.files["file"]                    
        if file:
            filename, file_extension = os.path.splitext(file.filename)
            file_save_name = str(uuid.uuid4().hex)+secure_filename(file.filename)
            message_data = {
                "sender_id": current_user._id,
                "conversation_id": conversation._id,
                "message": request.form['message'],
                "message_type": 'has_attachment',
            }
            message = Messages(**message_data)
            result = message.insert()
            if result is not None:
                file.save(os.path.join(app.config['FILE_FOLDER'], file_save_name))
                attachment_data = {
                    "message_id": result.inserted_id,
                    "file_extention": file_extension,
                    "file_path": os.path.join(app.config['FILE_FOLDER'], file_save_name),
                    "file_name": filename,
                }
                attachment = Attachment(**attachment_data)
                if attachment.insert():
                    participants = Participants.get_by_conversation(id_conversation)
                    message_inserted = Messages.get_message_and_sender(result.inserted_id)
                    json_mess = json.loads(json_util.dumps(message_inserted))
                    for participant in participants:
                        sendMessageTo(participant['user_id'], json_mess)
                    return "success", 200
        return request.form, 200
    return "failed", 400
@app.route('/new-chat/friends', methods=['POST'])
@login_required
def search_friends_for_new_chat():
    if 'name' in request.form:
        data = Friend.get_friend_by_id(current_user._id, scopeName=request.form['name'])
        return dumps(data)
    else:
        data = Friend.get_friend_by_id(current_user._id)
    return dumps(data)

@app.route('/new-chat/friends/<friend_id>', methods=['POST', 'GET'])
@login_required
def new_chat_with_friend(friend_id):
    conversation = Conversation.get_private_conversation(current_user._id, friend_id)
    friend = User.get_by_id(friend_id)
    if conversation:
        return dumps(conversation)
    else:
        conversation_id = Conversation.create_private()
        Participants.create_participant(conversation_id, current_user, "Private message")
        Participants.create_participant(conversation_id, friend, "Private message")
        conversation = Conversation.get_private_conversation(current_user._id, friend_id)

        return dumps(conversation)

########## TEST AREA ########################
@app.route("/get_list_conversation/<id_user>")
def get_list_conversation(id_user):
    return dumps(Conversation.get_list_conversation(id_user))

@app.route("/get_list_message/<id_conversation>")
def get_list_message(id_conversation):
    return dumps(Messages.get_list_message(id_conversation))
@app.route("/video-call/<room_id>")
def video_call(room_id):
    return render_template('call/video.html', title="Gọi video trên Hexam", room_id=room_id)