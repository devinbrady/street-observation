import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager


db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.static_folder = 'static'

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    from . import models

    with app.app_context():

        from . import routes
        from . import observations
        from . import sessions
        from . import counter
        from . import locations
        from . import distance
        
        db.create_all()

        return app

