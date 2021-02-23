import os
import pandas as pd
from dateutil import tz
from datetime import datetime

from flask import current_app as app
from flask import request, render_template, send_from_directory, Response


import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


from . import models
from . import db


local_timezone = 'America/New_York'


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('problem.html', e=e), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

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
    speed_limit_mph = request.form.get('speed_limit_mph')
    distance_miles = request.form.get('distance_miles')

    session_id = models.generate_uuid()
    session_mode = 'solo'

    solo_session = models.ObservationSession(session_id, session_mode, full_name, email, speed_limit_mph, distance_miles)
    db.session.add(solo_session)
    db.session.commit()

    return render_template(
        'session.html'
        , timer_status='ready_to_start'
        , session_id=session_id
        , distance_miles=distance_miles
        , vehicle_count=0
        , max_speed=None
        , median_speed=None
        , df=pd.DataFrame()
        )



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
            obs = models.Observation(observation_id=observation_id, session_id=session_id, start_time=utc_time)

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

            # mph = float(distance_miles) / (elapsed_seconds / 60 / 60)
            
            this_obs.update({
                models.Observation.end_time: utc_time
                , models.Observation.elapsed_seconds: elapsed_seconds
                # , models.Observation.mph: mph
                })
            db.session.commit()

            observation_id = None
            timer_status = 'ready_to_start'
    

    df = pd.read_sql(
        f'''
        select
        o.start_time
        , o.end_time
        , o.elapsed_seconds
        , o.valid
        , s.distance_miles

        from observations o
        inner join sessions s using (session_id)

        where s.session_id = '{session_id}'
        and o.end_time is not null

        order by o.start_time desc
        '''
        , db.session.bind
        )


    vehicle_count = len(df)

    if vehicle_count == 0:
        max_speed = 0
        median_speed = 0
    else:

        df['mph'] = df['distance_miles'] / (df['elapsed_seconds'] / 60 / 60)
        df['start_time_local'] = (
            df['start_time']
            .dt.tz_localize('UTC')
            .dt.tz_convert(local_timezone)
            .dt.strftime('%l:%M:%S %p')
            )

        valid_observations = df[df.valid].copy()

        max_speed = valid_observations.mph.max()
        median_speed = valid_observations.mph.median()


    return render_template(
        'session.html'
        , session_id=session_id
        , observation_id=observation_id
        , timer_status=timer_status
        , vehicle_count=vehicle_count
        , max_speed=max_speed
        , median_speed=median_speed
        , distance_miles=distance_miles
        , elapsed_seconds=elapsed_seconds
        , df=df
        )


# @app.route('observation/<observation_id>', methods=['POST'])
# def toggle_valid():
#     validation_action = request.args.get('validation_action', type=bool)





@app.route('/session/<session_id>/plot.png')
def plot_png(session_id):
    fig = create_histogram(session_id)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_histogram(session_id):

    session_observations = pd.read_sql(
        f'''
        select
        o.elapsed_seconds
        , s.distance_miles

        from observations o
        inner join sessions s using (session_id)

        where s.session_id = '{session_id}'
        and o.end_time is not null
        and o.valid
        '''
        , db.session.bind
        )

    session_observations['mph'] = session_observations['distance_miles'] / (session_observations['elapsed_seconds'] / 60 / 60)

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.hist(session_observations['mph'])

    axis.yaxis.set_major_locator(MaxNLocator(integer=True))
    axis.set_ylabel('Count of Vehicles')
    axis.set_xlabel('MPH')

    return fig


@app.route('/observation/<observation_id>', methods=['GET', 'POST'])
def render_observation(observation_id):

    if request.method == 'POST':

        valid_action = request.args.get('valid_action')

        update_query = f'''
            update observations
            set valid = {valid_action}
            where observation_id = '{observation_id}'
        '''

        resp = db.engine.execute(update_query)
        # How to confirm this?



    this_obs = pd.read_sql(
        f'''
        select
        o.start_time
        , o.end_time
        , o.elapsed_seconds
        , o.valid
        , s.session_id
        , s.distance_miles
        , s.speed_limit_mph

        from observations o
        inner join sessions s using (session_id)

        where o.observation_id = '{observation_id}'
        '''
        , db.session.bind
        )

    this_obs['mph'] = this_obs['distance_miles'] / (this_obs['elapsed_seconds'] / 60 / 60)
    this_obs['start_time_local'] = (
        this_obs['start_time']
        .dt.tz_localize('UTC')
        .dt.tz_convert(local_timezone)
        .dt.strftime('%l:%M:%S %p')
        )

    this_obs['start_date_local'] = (
        this_obs['start_time']
        .dt.tz_localize('UTC')
        .dt.tz_convert(local_timezone)
        .dt.strftime('%b %w, %Y')
        )

    this_obs_series = this_obs.squeeze()

    return render_template(
        'observation.html'
        , observation_id=observation_id
        , session_id=this_obs_series['session_id']
        , start_date_local=this_obs_series['start_date_local']
        , start_time_local=this_obs_series['start_time_local']
        , distance_miles=this_obs_series['distance_miles']
        , elapsed_seconds=this_obs_series['elapsed_seconds']
        , mph=this_obs_series['mph']
        , speed_limit_mph=this_obs_series['speed_limit_mph']
        , valid=this_obs_series['valid']
        )
