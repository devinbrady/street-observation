import os
from dateutil import tz
from datetime import datetime

from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%s:%s@%s/%s' % (
    # ARGS.dbuser, ARGS.dbpass, ARGS.dbhost, ARGS.dbname
    os.environ['DBUSER'], os.environ['DBPASS'], os.environ['DBHOST'], os.environ['DBNAME']
)

# initialize the database connection
DB = SQLAlchemy(app)

# initialize database migration management
MIGRATE = Migrate(app, DB)

local_timezone = 'America/New_York'

from models import *


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

