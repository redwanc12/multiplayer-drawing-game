from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import JoinForm, HostForm
from .. import db
from .models import Room, User

import random
import string

@main.route('/', methods=['GET', 'POST'])
def index():
    #log in form
    form = JoinForm()
    if form.validate_on_submit():
        room_name = form.room.data
        room = db.session.query(Room).get(room_name)
        if(not room): #fix this
            return "room does not exist."
        elif(room.game_started):
            return "Cant join room because game has already started."
        elif(form.name.data in [u.name for u in room.users]):
                return "someone in that room has that name.. Choose a different one."
        else:
            new_user = User(name=form.name.data, points=0, room=room)
            db.session.add(new_user)
            db.session.commit()
            session['name'] = form.name.data
            session['room'] = form.room.data
            session['userID'] = new_user.id
            session['color'] = "%06x" % random.randint(0, 0xFFFFFF) #generates a random color
            return redirect(url_for('.chat'))

    #host form
    hostForm = HostForm()
    if hostForm.validate_on_submit():
        room_name = generateCode()
        room = db.session.query(Room).get(room_name)
        while(room): 
            #creates new code is room alerady exist
            room_name = generateCode()
            room = db.session.query(Room).filter(Room.name == room_name) 
        new_room = Room(name=room_name)
        db.session.add(new_room)
        new_user = User(name=hostForm.name.data, points=0, room=new_room)
        db.session.add(new_user)
        db.session.commit()
        new_room.host_id = new_user.id
        db.session.commit()
        session['name'] = hostForm.name.data
        session['room'] = room_name
        session['userID'] = new_user.id
        session['color'] = "%06x" % random.randint(0, 0xFFFFFF) #generates a random color
        return redirect(url_for('.chat'))

    return render_template('index.html', form=form, hostForm=hostForm)


@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)


def generateCode():
    #TODO: move this function to another file
    return ''.join([random.choice(string.ascii_letters 
                    ) for n in range(3)] + [random.choice(string.digits) for n in range(3)]).upper() 