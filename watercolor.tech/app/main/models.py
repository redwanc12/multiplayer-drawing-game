from .. import db

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer)
    name = db.Column(db.String(200), unique=True, nullable=False, primary_key=True)
    game_started = db.Column(db.Boolean)
    current_drawer_index = db.Column(db.Integer)
    current_word = db.Column(db.String(15))
    host_id = db.Column(db.Integer)
    users = db.relationship('User', backref='room')
    
    def __init__(self, name, game_started=False, current_drawer_index=0):
        self.name = name
        self.game_started = game_started
        self.current_drawer_index = current_drawer_index

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer)
    room_name = db.Column(db.String, db.ForeignKey('room.name'))