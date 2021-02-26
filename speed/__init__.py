import os

from flask import Flask
# from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


db = SQLAlchemy()

socketio = SocketIO()
    

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.static_folder = 'static'

    db.init_app(app)

    socketio.init_app(app)

    # bootstrap = Bootstrap(app)


    from . import models

    with app.app_context():

        from . import routes
        db.create_all()

        return app

