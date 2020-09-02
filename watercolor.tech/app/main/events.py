from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio, db
from .models import Room, User

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    emit('message', {
        'color': session.get('color'), 
        'msg': "has joined the room", 
        'name':session.get('name'),
        'special':True
        }, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    if message['msg'] == db.session.query(Room).get_or_404(room).current_word:
        if(session.get(message['msg']) != True):
            curr_user = db.session.query(User).get_or_404(session.get('userID'))
            curr_user.points += message['timeLeft']
            db.session.commit()
            emit(
                'message', {'color': session.get('color'), 
                'msg': "HAS GUESSED THE WORD!", 
                'name':session.get('name'),
                'special': True
            }, room=room)
            get_info()
            session[message['msg']] = True
    else:
        emit(
            'message', {'color': session.get('color'), 
            'msg': message['msg'], 
            'name':session.get('name'),
            'special': False
        }, room=room)


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('message', {
    'color': session.get('color'), 
    'msg': "has left the room", 
    'name':session.get('name'),
    'special':True
    }, room=room)
    curr_user = db.session.query(User).get_or_404(session.get('userID'))
    db.session.delete(curr_user)
    db.session.commit()
    room_db = db.session.query(Room).get_or_404(room)
    if(len(room_db.users) == 0):
        db.session.delete(room_db)
        db.session.commit()
    else:
        get_info()

@socketio.on("getInfo", namespace='/chat')
def get_info():
    room = db.session.query(Room).get_or_404(session.get('room'))
    host = User.query.get_or_404(room.host_id)
    userlist = [[u.name, u.points] for u in sorted(room.users, key=lambda u: u.id)]
    data = {
        "Users":userlist, 
        "Host":host.name, 
        "game_started":room.game_started, 
        "current_drawer": userlist[room.current_drawer_index][0],
        "username": session.get('name')
    }
    emit("getInfo", data, room=room.name)

@socketio.on('drawCanvas', namespace='/chat')
def update_canvas(data):
    emit('drawCanvas', data, room=session.get('room'))

@socketio.on('updateColor', namespace='/chat')
def update_color(data):
    emit('updateColor', data, room=session.get('room'))

@socketio.on('updatePrev', namespace='/chat')
def update_prev(data):
    emit('updatePrev', data, room=session.get('room'))

@socketio.on('updateBrushSize', namespace='/chat')
def update_brush_size(data):
    emit('updateBrushSize', data, room=session.get('room'))

@socketio.on('clearCanvas', namespace='/chat')
def clear_canvas():
    emit('clearCanvas', room=session.get('room'))

@socketio.on('startGame', namespace='/chat')
def start_game(word):
    print('startGame')
    room = session.get('room')
    session[word] = True
    roomdb = db.session.query(Room).get_or_404(room)
    roomdb.current_word = word
    roomdb.game_started = True
    db.session.commit()
    emit('message', {
        'color': session.get('color'), 
        'msg': "is now drawing!",
        'name':session.get('name'),
        'special':True
        }, room=room)
    emit("startGame", word, room=room)

@socketio.on('nextRound', namespace='/chat')
def next_round():
    reset_timer()
    clear_canvas()
    room = db.session.query(Room).get_or_404(session.get('room'))
    room.current_drawer_index += 1
    room.current_word = None
    db.session.commit()
    if(room.current_drawer_index == len(room.users)):
        end_game()
    else:
        get_info()
        emit('nextRound', room=room.name)

@socketio.on('resetTimer', namespace='/chat')
def reset_timer():
    emit('resetTimer', room=session.get('room'))

def end_game():
    room = db.session.query(Room).get_or_404(session.get('room'))
    winner = sorted(room.users, key=lambda u: u.points)[-1].name
    emit('endGame', winner, room=session.get('room'))
    destroy_room()

def destroy_room():
    room = db.session.query(Room).get_or_404(session.get('room'))
    for user in room.users:
        db.session.delete(user)
    db.session.delete(room)
    db.session.commit()