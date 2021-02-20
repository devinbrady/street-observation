import os
from dateutil import tz
from datetime import datetime

from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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



# initialize the database connection
# TODO: use g
DB = SQLAlchemy(app)

# initialize database migration management
MIGRATE = Migrate(app, DB)

local_timezone = 'America/New_York'

# from models import *


@app.route('/', methods = ['GET'])
def display_index():
    return render_template('index.html')

@app.route('/begin_solo', methods = ['GET'])
def display_begin_solo():
    return render_template('begin_solo.html')

@app.route('/begin_solo', methods = ['POST'])
def register_solo_session():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    distance_miles = request.form.get('distance_miles')

    session_id = generate_uuid()
    session_mode = 'solo'

    solo_session = Session(session_id, session_mode, full_name, email, distance_miles)
    DB.session.add(solo_session)
    DB.session.commit()

    return render_template('session.html', timer_status='ready_to_start', session_id=session_id, distance_miles=distance_miles)



@app.route('/session', methods = ['GET'])
def view_session():
    return render_template('session.html', timer_status='ready_to_start')



@app.route('/session', methods=['POST'])
def post_time():

    timer_type = request.args.get('timer', default=None, type=str)
    session_id = request.args.get('session_id', default=None, type=str)
    obs_id = request.args.get('obs_id', default=None, type=str)
    distance_miles = request.args.get('distance_miles', default=None, type=str)
    
    
    if timer_type:

        utc_time = datetime.utcnow()

        if timer_type == 'start':
            obs_id = generate_uuid()
            obs = Obs(obs_id=obs_id, session_id=session_id, start_time=utc_time, distance_miles=distance_miles)

            DB.session.add(obs)
            DB.session.commit()

            elapsed_seconds = None
            mph = None

            timer_status = 'vehicle_in_timer'


        elif timer_type == 'end':

            this_obs = DB.session.query(Obs).filter(Obs.obs_id == obs_id)
            
            # Calculate time and speed
            elapsed_td = utc_time - this_obs.scalar().start_time
            elapsed_seconds = elapsed_td.total_seconds()

            mph = float(distance_miles) / (elapsed_seconds / 60 / 60)
            
            this_obs.update({
                Obs.end_time: utc_time
                , Obs.elapsed_seconds: elapsed_seconds
                , Obs.mph: mph
                })
            DB.session.commit()

            obs_id = None
            timer_status = 'ready_to_start'
    

    observations = (
        DB.session
        .query(Obs)
        .filter(
            Obs.session_id == session_id
            , Obs.end_time != None
            )
        .order_by(Obs.start_time.desc())
        .all()
        )

    for o in observations:
        local_ts = (
            o.start_time
            .replace(tzinfo=tz.gettz('UTC'))
            .astimezone(tz.gettz(local_timezone))
            )

        o.start_time_local = local_ts.strftime('%l:%M:%S %p')
    # .replace(tzinfo=from_zone)

    return render_template(
        'session.html'
        , session_id=session_id
        , obs_id=obs_id
        , timer_status=timer_status
        , distance_miles=distance_miles
        , elapsed_seconds=elapsed_seconds
        , mph=mph
        , observations=observations
        )





# from app import DB
# from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


def generate_uuid():
    return str(uuid.uuid4())



class Session(DB.Model):
    """Record info about a session of observations"""

    __tablename__ = 'sessions'
    session_id = DB.Column(UUID(as_uuid=True), primary_key=True)
    session_mode = DB.Column(DB.String(20))
    full_name = DB.Column(DB.String(80))
    email = DB.Column(DB.String(120))
    distance_miles = DB.Column(DB.Float)
    created_at = DB.Column(DB.DateTime)

    def __init__(self, session_id, session_mode, full_name=None, email=None, distance_miles=None):

        self.session_id = session_id
        self.session_mode = session_mode
        self.full_name = full_name
        self.email = email
        self.distance_miles = distance_miles
        self.created_at = datetime.utcnow()




class Obs(DB.Model):
    """Record the start and stop time of each car"""

    __tablename__ = 'obs'
    obs_id = DB.Column(UUID(as_uuid=True), primary_key=True)
    session_id = DB.Column(UUID(as_uuid=True))
    # valid = True

    # observer_a_lat
    # observer_a_lon
    # observer_b_lat
    # observer_b_lon
    distance_miles = DB.Column(DB.Float)
    start_time = DB.Column(DB.DateTime)
    end_time = DB.Column(DB.DateTime)
    elapsed_seconds = DB.Column(DB.Float)
    mph = DB.Column(DB.Float)


    def __init__(self, obs_id, session_id, distance_miles=None, start_time=None, end_time=None, elapsed_seconds=None, mph=None):

        self.obs_id = obs_id
        self.session_id = session_id
        self.distance_miles = distance_miles
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_seconds = elapsed_seconds
        self.mph = mph
