from bson.objectid import ObjectId
from app import socketio
from flask_socketio import send, emit
from flask_socketio import join_room, leave_room
import flask_login
from flask import request

clients = dict()

def sendMessageTo(user_id, data):
    
    if str(user_id) in clients:
        sid = clients[str(user_id)]
        socketio.emit("chat message", data, room=sid)
        print("SEND MESSAGE SUCCESS")

@socketio.on('connect')
def on_connect():
    if flask_login.current_user.is_authenticated:
        user_id = str(flask_login.current_user._id)
        clients[user_id] = request.sid
    print("Current Clients: ")
    print(clients)
@socketio.on('disconnect')
def on_disconnect():
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user._id
        del clients[str(user_id)]
    print("Current Clients: ")
    print(clients)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('my event')
def handle_my_custom_event(json):
    
    if flask_login.current_user.is_authenticated:
        print(flask_login.current_user.username)
    print('received "my event": ' + str(json))

@socketio.on('user_send_message')
def handle_my_custom_event(json):
    print('received "user_send_message": ' + str(json))
    message_back = {
        "type": "send back",
        "message": "toi da nhan dc message"
    }
    send(message_back, json=True)