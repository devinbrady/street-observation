import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# initialize the database connection
db = SQLAlchemy()



def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.static_folder = 'static'

    db.init_app(app)


    from . import models

    with app.app_context():

        from . import routes
        db.create_all()

        return app

