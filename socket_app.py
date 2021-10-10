from app import socketio
from flask_socketio import send, emit
from flask_socketio import join_room, leave_room
import flask_login


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