import os
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

socketio = SocketIO()
db = SQLAlchemy()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    # app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2250@localhost/rooms'
    app.config['SECRET_KEY'] = os.environ.get("SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

