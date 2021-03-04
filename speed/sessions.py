
import io
import os
import pandas as pd
from dateutil import tz
from datetime import datetime, timezone

from sqlalchemy import text
from flask_socketio import emit, join_room
from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response, abort

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from . import models
from . import dataframes
from . import db, socketio
from .forms import SessionSettingsForm
from .observations import toggle_valid



@app.route('/session_settings', methods=['GET', 'POST'])
def edit_session_settings():
    """
    Receive information about each session
    """

    location_id = request.args.get('location_id')
    session_id = request.args.get('session_id')

    if not session_id:
        session_id = 'new_session'


    if session_id == 'new_session':
        # New session

        form = SessionSettingsForm(
            speed_limit_mph=20
            , distance_value=100
            , distance_units='feet'
            , session_mode='pair'
            )
    
        if form.validate_on_submit():

            session_id = models.generate_uuid()

            distance_miles = convert_distance_units(form.distance_value.data, form.distance_units.data)

            local_timezone = models.get_location_timezone(location_id)

            new_session_object = models.ObservationSession(
                session_id=session_id
                , location_id=location_id
                , session_mode=form.session_mode.data
                , speed_limit_mph=form.speed_limit_mph.data
                , distance_miles=distance_miles
                , session_description=form.session_description.data
                , local_timezone=local_timezone
                )
            db.session.add(new_session_object)
            db.session.commit()

            return redirect(f'session?session_id={session_id}')

    else:
        # Existing session
        with open(os.path.join(app.root_path, 'queries/sessions_one.sql'), 'r') as f:
            settings_df = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

        settings = settings_df.squeeze()

        form = SessionSettingsForm(
            speed_limit_mph=settings['speed_limit_mph']
            , distance_value=settings['distance_miles']
            , distance_units='miles'
            , session_mode=settings['session_mode']
            , session_description=settings['session_description']
            )

        if form.validate_on_submit():

            distance_miles = convert_distance_units(form.distance_value.data, form.distance_units.data)

            with open(os.path.join(app.root_path, 'queries/sessions_update.sql'), 'r') as f:
                result = db.engine.execute(
                    text(f.read())
                    , session_id=session_id
                    , distance_miles=distance_miles
                    , speed_limit_mph=form.speed_limit_mph.data
                    , session_mode=form.session_mode.data
                    , session_description=form.session_description.data
                    )

            return redirect(f'session?session_id={session_id}')

    
    return render_template(
        'session_settings.html'
        , form=form
        , location_id=location_id
        , session_id=session_id
        )



def convert_distance_units(value, unit):
    """
    Return a distance value in miles
    """

    if unit == 'feet':
        return value / 5280
    else:
        return value



@app.route('/session_list', methods=['GET'])
def list_sessions():
    """
    List all sessions
    """

    with open(os.path.join(app.root_path, 'queries/sessions_list.sql'), 'r') as f:
        sessions = pd.read_sql(text(f.read()), db.session.bind)

    if len(sessions) > 0:

        sessions = dataframes.format_in_local_time(
            sessions, 'first_start', 'local_timezone', 'start_timestamp_local', '%Y-%m-%d %l:%M:%S %p %Z')

    return render_template(
        'session_list.html'
        , sessions=sessions
        )



@socketio.on('connect')
def new_socket_connection():
    """
    When a new user connects via websocket, assign them to a room based on the session_id
    """
    join_room(session['session_id'])



@socketio.on('broadcast start')
def broadcast_start(message):
    """
    A new observation has been initiated
    """
    session_id = message['session_id']
    # location_id = message['location_id']

    # join_room(session_id)

    utc_time = datetime.now(tz=timezone.utc)

    active_observation_id = models.generate_uuid()
    session_timezone = models.get_session_timezone(session_id)
    obs = models.Observation(observation_id=active_observation_id, session_id=session_id, start_time=utc_time, local_timezone=session_timezone)

    db.session.add(obs)
    db.session.commit()

    emit(
        'new observation id'
        , {'active_observation_id': active_observation_id}
        , room=session['session_id']
        , broadcast=True
        )



@socketio.on('broadcast end')
def broadcast_end(message):
    """
    The timer has ended for an observation
    """
    session_id = message['session_id']
    active_observation_id = message['active_observation_id']

    if active_observation_id == 'no_active_obs':
        print('No active observation ID passed')
        abort(500)

    utc_time = datetime.now(tz=timezone.utc)

    this_obs = db.session.query(models.Observation).filter(models.Observation.observation_id == active_observation_id)
    
    # Calculate time
    elapsed_td = utc_time - this_obs.scalar().start_time
    elapsed_seconds = elapsed_td.total_seconds()
    
    this_obs.update({
        models.Observation.end_time: utc_time
        , models.Observation.elapsed_seconds: elapsed_seconds
        })
    db.session.commit()

    emit(
        'observation concluded'
        , room=session['session_id']
        , broadcast=True
        )



@app.route('/session', methods=['GET', 'POST'])
def session_handler():

    session_id = request.args.get('session_id')

    # A session_id needs to be provided to view this page
    if not session_id:
        abort(404)

    session['session_id'] = session_id

    with open(os.path.join(app.root_path, 'queries/observations_list.sql'), 'r') as f:
        observations = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

    completed_observations = observations[observations.end_time.notnull()].copy()

    # with open(os.path.join(app.root_path, 'queries/locations_one.sql'), 'r') as f:
    #     locations_df = pd.read_sql(text(f.read()), db.session.bind, params={'location_id': location_id})
    #     this_location = locations_df.squeeze()


    if len(observations) == 0:

        vehicle_count = 0
        max_speed = 0
        median_speed = 0
        speed_limit_mph = 0
        distance_miles = 0

    elif len(observations) == 1 and len(completed_observations) == 0:
        # first time through, timer_status = 'vehicle_in_timer'

        vehicle_count = 0
        max_speed = 0
        median_speed = 0
        speed_limit_mph = observations.speed_limit_mph.median()
        distance_miles = observations.distance_miles.median()

    else:

        completed_observations['mph'] = completed_observations['distance_miles'] / (completed_observations['elapsed_seconds'] / 60 / 60)

        completed_observations = dataframes.format_in_local_time(completed_observations, 'start_time', 'local_timezone', 'start_date_local', '%b %w, %Y')
        completed_observations = dataframes.format_in_local_time(completed_observations, 'start_time', 'local_timezone', 'start_time_local', '%l:%M:%S %p')


        valid_observations = completed_observations[completed_observations.observation_valid].copy()
        vehicle_count = len(valid_observations)
        max_speed = valid_observations.mph.max()
        median_speed = valid_observations.mph.median()
        distance_miles = observations.distance_miles.median()
        speed_limit_mph = observations.speed_limit_mph.median()

    return render_template(
        'session.html'
        , session_id=session_id
        # , location_name=location_name
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

    return redirect(f'/session?session_id={session_id}')



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

    todo: this query is basically run twice on the session page. find way to consolidate
    """

    with open(os.path.join(app.root_path, 'queries/observations_histogram.sql'), 'r') as f:
        session_observations = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

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



