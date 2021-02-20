import os
from dateutil import tz
from datetime import datetime

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy


# initialize the database connection
db = SQLAlchemy()



def create_app(test_config=None):

    app = Flask(__name__)
    app.static_folder = 'static'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



    if 'GAE_INSTANCE' in os.environ:
        # Running in Google App Engine

        # Remember - storing secrets in plaintext is potentially unsafe. Consider using
        # something like https://cloud.google.com/secret-manager/docs/overview to help keep
        # secrets secret.
        db_user = os.environ["DBUSER"]
        db_pass = os.environ["DBPASS"]
        db_name = os.environ["DBNAME"]
        db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
        cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

        # Equivalent URL:
        # postgres+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<socket_path>/<cloud_sql_instance_name>/.s.PGSQL.5432

        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={db_socket_dir}/{cloud_sql_connection_name}/.s.PGSQL.5432'

    else:
        # Assume we're running locally

        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%s:%s@%s/%s' % (
            # ARGS.dbuser, ARGS.dbpass, ARGS.dbhost, ARGS.dbname
            os.environ['DBUSER'], os.environ['DBPASS'], os.environ['DBHOST'], os.environ['DBNAME']
        )

    db.init_app(app)



    local_timezone = 'America/New_York'

    from . import models

    with app.app_context():

        from . import routes

        return app


