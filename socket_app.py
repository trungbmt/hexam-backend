from bson.objectid import ObjectId
from app import socketio
from flask_socketio import send, emit
from flask_socketio import join_room, leave_room
import flask_login
from flask import request

clients = dict()
peers = dict()

def sendMessageTo(user_id, data):
    
    socketio.emit("chat message", data, to=str(user_id))
    print("SEND MESSAGE SUCCESS" + str(user_id))
    # if str(user_id) in clients:
    #     sid = clients[str(user_id)]
    #     socketio.emit("chat message", data, room=sid)
    #     print("SEND MESSAGE SUCCESS")

@socketio.on('connect')
def on_connect():
    if flask_login.current_user.is_authenticated:
        user_id = str(flask_login.current_user._id)
        join_room(user_id)
        print("join room:" +user_id)
        # clients[user_id] = request.sid
    # print("Current Clients: ")
    # print(clients)

@socketio.on('disconnect')
def on_disconnect():
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user._id
        leave_room(user_id)
        # del clients[str(user_id)]
    # print(request.sid + " disconnected")
    # print("Current Clients: ")
    # print(clients)

@socketio.on('toggle-stream')
def on_toggle_stream(room, data):
    data['peerID'] = str(flask_login.current_user._id)
    emit('toggle-stream', data, to=room)

@socketio.on('join')
def on_join(room, peerId):
    join_room(room)
    print(peerId + ' has entered the room {}.'.format(room))
    emit('user-connected', peerId, to=room)
    peers[request.sid] = peerId

    @socketio.on('disconnect')
    def disconnect_room():
        leave_room(room)
        if request.sid in peers:
            peerId2 = peers[request.sid]
            emit('user-disconnected', peerId2, to=room)
            print(peerId2 + ' has left the room {}.'.format(room))
            del peers[request.sid]

@socketio.on('leave')
def on_leave(room, peerId):
    leave_room(room)
    emit('user-disconnected', peerId, to=room)
    print(peerId + ' has left2 the room {}.'.format(room))

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