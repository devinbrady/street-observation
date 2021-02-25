import os
import pandas as pd
from dateutil import tz
from datetime import datetime

from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response


import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


from . import models
from . import db
from .forms import SessionSettingsForm

from sqlalchemy import text


local_timezone = 'America/New_York'


@app.route('/session_settings', methods=['GET', 'POST'])
def edit_session_settings():
    """
    Receive information about each session
    """

    session_id = request.args.get('session_id')
    if not session_id:
        session_id = 'new_session'


    if session_id == 'new_session':
        # New session

        form = SessionSettingsForm(
            speed_limit_mph=20
            , distance_miles=0.01
            )
    
        if form.validate_on_submit():

            session_id = models.generate_uuid()
            session_mode = 'solo'

            solo_session = models.ObservationSession(
                session_id
                , session_mode
                , form.full_name.data
                , form.email.data
                , form.speed_limit_mph.data
                , form.distance_miles.data
                )
            db.session.add(solo_session)
            db.session.commit()

            return render_template(
                'session.html'
                , timer_status='ready_to_start'
                , session_id=session_id
                , vehicle_count=0
                , max_speed=0
                , median_speed=0
                , df=pd.DataFrame()
                )

    else:
        # Existing session
        query = f'''
            select
            full_name
            , email
            , speed_limit_mph
            , distance_miles

            from sessions
            where session_id = '{session_id}'
        '''

        settings_df = pd.read_sql(query, db.session.bind)
        settings = settings_df.squeeze()

        form = SessionSettingsForm(
            full_name=settings['full_name']
            , email=settings['email']
            , speed_limit_mph=settings['speed_limit_mph']
            , distance_miles=settings['distance_miles']
            )

        if form.validate_on_submit():
            t = text('''
                update sessions
                set 
                    full_name = :full_name
                    , email = :email
                    , distance_miles = :distance_miles
                    , speed_limit_mph = :speed_limit_mph

                where session_id = :session_id
                ''')

            result = db.engine.execute(
                t
                , session_id=session_id
                , full_name=form.full_name.data
                , email=form.email.data
                , distance_miles=form.distance_miles.data
                , speed_limit_mph=form.speed_limit_mph.data
                )

            return session_handler(session_id)

    
    return render_template(
        'session_settings.html'
        , form=form
        , session_id=session_id
        )



@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('problem.html', e=e), e.code

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/', methods=['GET'])
def display_index():
    return render_template('index.html')


@app.route('/session_list', methods=['GET'])
def list_sessions():
    sessions = pd.read_sql(
        f'''
        select
        s.session_id
        , s.distance_miles
        , min(o.start_time) as first_start
        , count(o.*) as num_observations

        from observations o
        inner join sessions s using (session_id)

        where o.valid
        and o.end_time is not null

        group by s.session_id, s.distance_miles
        order by first_start desc
        '''
        , db.session.bind
        )

    sessions['start_timestamp_local'] = (
        sessions['first_start']
        .dt.tz_localize('UTC')
        .dt.tz_convert(local_timezone)
        .dt.strftime('%Y-%m-%d %l:%M:%S %p')
        )


    return render_template(
        'session_list.html'
        , sessions=sessions
        )



@app.route('/session/<session_id>', methods=['GET', 'POST'])
def session_handler(session_id):

    timer_type = request.args.get('timer', default=None, type=str)
    active_observation_id = request.args.get('active_observation_id', default=None, type=str)
    

    # print("browser time: ")
    # print(request.args.get("time"))
    # print("server time : ")
    # print(datetime.utcnow().strftime('%A %B, %d %Y %H:%M:%S'))
    
    if timer_type:

        utc_time = datetime.utcnow()

        if timer_type == 'start':
            active_observation_id = models.generate_uuid()
            obs = models.Observation(observation_id=active_observation_id, session_id=session_id, start_time=utc_time)

            db.session.add(obs)
            db.session.commit()

            timer_status = 'vehicle_in_timer'


        elif timer_type == 'end':

            this_obs = db.session.query(models.Observation).filter(models.Observation.observation_id == active_observation_id)
            
            # Calculate time
            elapsed_td = utc_time - this_obs.scalar().start_time
            elapsed_seconds = elapsed_td.total_seconds()

            
            this_obs.update({
                models.Observation.end_time: utc_time
                , models.Observation.elapsed_seconds: elapsed_seconds
                })
            db.session.commit()

            active_observation_id = None
            timer_status = 'ready_to_start'

        elif timer_type == 'ready':
            timer_status = 'ready_to_start'
    
    else:
        timer_status = 'timer_off'


    observations = pd.read_sql(
        f'''
        select
        o.observation_id
        , o.start_time
        , o.end_time
        , o.elapsed_seconds
        , o.valid
        , s.distance_miles
        , s.speed_limit_mph

        from observations o
        inner join sessions s using (session_id)

        where s.session_id = '{session_id}'

        order by o.start_time desc
        '''
        , db.session.bind
        )

    completed_observations = observations[observations.end_time.notnull()].copy()

    num_observations = len(observations)

    if len(observations) == 1 and len(completed_observations) == 0:
        # first time through, timer_status = 'vehicle_in_timer'

        vehicle_count = 0
        max_speed = 0
        median_speed = 0
        speed_limit_mph = observations.speed_limit_mph.median()
        distance_miles = observations.distance_miles.median()

    else:

        completed_observations['mph'] = completed_observations['distance_miles'] / (completed_observations['elapsed_seconds'] / 60 / 60)
        completed_observations['start_time_local'] = (
            completed_observations['start_time']
            .dt.tz_localize('UTC')
            .dt.tz_convert(local_timezone)
            .dt.strftime('%l:%M:%S %p')
            )

        valid_observations = completed_observations[completed_observations.valid].copy()
        vehicle_count = len(valid_observations)
        max_speed = valid_observations.mph.max()
        median_speed = valid_observations.mph.median()
        distance_miles = observations.distance_miles.median()
        speed_limit_mph = observations.speed_limit_mph.median()

    return render_template(
        'session.html'
        , session_id=session_id
        , active_observation_id=active_observation_id
        , timer_status=timer_status
        , vehicle_count=vehicle_count
        , max_speed=max_speed
        , median_speed=median_speed
        , speed_limit_mph=speed_limit_mph
        , distance_miles=distance_miles
        , df=completed_observations
        )



@app.route('/session/<session_id>/<observation_id>', methods=['POST'])
def toggle_valid_on_list(session_id, observation_id):
    """
    When on a session page with a list of observations, toggle the validity of one observation
    """

    valid_action = request.args.get('valid_action')
    toggle_valid(observation_id, valid_action)

    return session_handler(session_id)



@app.route('/session/<session_id>/plot.png')
def plot_png(session_id):
    """
    For one session_id, create a histogram and output it in bytes for display as an image
    """
    fig = create_histogram(session_id)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



def create_histogram(session_id):
    """
    Create a Matplotlib figure for a histogram of speeds observed in one session
    """

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
    fig.set_size_inches(5, 4)
    axis = fig.add_subplot(1, 1, 1)
    axis.hist(session_observations['mph'])

    axis.yaxis.set_major_locator(MaxNLocator(integer=True))
    axis.set_title('Histogram of Observed Speeds')
    axis.set_ylabel('Count of Vehicles')
    axis.set_xlabel('MPH')

    return fig



@app.route('/observation/<observation_id>', methods=['GET', 'POST'])
def one_observation(observation_id):
    """
    Display information about one observation
    """

    if request.method == 'POST':
        valid_action = request.args.get('valid_action')
        toggle_valid(observation_id, valid_action)

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



def toggle_valid(observation_id, valid_action):
    """
    Change the validation status of a single observation in the database
    """

    update_query = text('''
        update observations
        set valid = :valid_action
        where observation_id = :observation_id
    ''')

    result = db.engine.execute(
        update_query
        , valid_action=valid_action
        , observation_id=observation_id
        )
    # How to confirm this?
