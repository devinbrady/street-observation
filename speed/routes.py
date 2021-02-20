from dateutil import tz
from datetime import datetime

from flask import current_app as app
from flask import request, render_template

from . import models
from . import db


local_timezone = 'America/New_York'


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

    session_id = models.generate_uuid()
    session_mode = 'solo'

    solo_session = models.Session(session_id, session_mode, full_name, email, distance_miles)
    db.session.add(solo_session)
    db.session.commit()

    return render_template('session.html', timer_status='ready_to_start', session_id=session_id, distance_miles=distance_miles)



@app.route('/session', methods = ['GET'])
def view_session():
    return render_template('session.html', timer_status='ready_to_start')



@app.route('/session', methods=['POST'])
def post_time():

    timer_type = request.args.get('timer', default=None, type=str)
    session_id = request.args.get('session_id', default=None, type=str)
    observation_id = request.args.get('observation_id', default=None, type=str)
    distance_miles = request.args.get('distance_miles', default=None, type=str)
    
    
    if timer_type:

        utc_time = datetime.utcnow()

        if timer_type == 'start':
            observation_id = models.generate_uuid()
            obs = models.Observation(observation_id=observation_id, session_id=session_id, start_time=utc_time, distance_miles=distance_miles)

            db.session.add(obs)
            db.session.commit()

            elapsed_seconds = None
            mph = None

            timer_status = 'vehicle_in_timer'


        elif timer_type == 'end':

            this_obs = db.session.query(models.Observation).filter(models.Observation.observation_id == observation_id)
            
            # Calculate time and speed
            elapsed_td = utc_time - this_obs.scalar().start_time
            elapsed_seconds = elapsed_td.total_seconds()

            mph = float(distance_miles) / (elapsed_seconds / 60 / 60)
            
            this_obs.update({
                models.Observation.end_time: utc_time
                , models.Observation.elapsed_seconds: elapsed_seconds
                , models.Observation.mph: mph
                })
            db.session.commit()

            observation_id = None
            timer_status = 'ready_to_start'
    

    observations = (
        db.session
        .query(models.Observation)
        .filter(
            models.Observation.session_id == session_id
            , models.Observation.end_time != None
            )
        .order_by(models.Observation.start_time.desc())
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
        , observation_id=observation_id
        , timer_status=timer_status
        , distance_miles=distance_miles
        , elapsed_seconds=elapsed_seconds
        , mph=mph
        , observations=observations
        )