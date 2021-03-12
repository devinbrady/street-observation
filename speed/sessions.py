
import io
import os
import segno
import pandas as pd

from sqlalchemy import text
from flask_socketio import emit, join_room
from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response, abort
from flask_login import login_required

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from . import models
from . import utilities
from . import db, socketio
from .forms import SessionSettingsForm
from .observations import toggle_valid



@app.route('/session_settings', methods=['GET', 'POST'])
@login_required
def edit_session_settings():
    """
    Receive information about each session
    """

    session_id = request.args.get('session_id')
    location_id = request.args.get('location_id')

    if not session_id:
        session_id = 'new_session'


    if session_id == 'new_session':

        if not location_id:
            print('The location_id must be specified to start a new session')
            abort(404)

        this_location = utilities.one_location(location_id)
        location_name = this_location['location_name']

        form = SessionSettingsForm(
            speed_limit_value=20
            , speed_units='miles per hour'
            , distance_value=100
            , distance_units='feet'
            , session_mode='speed timer'
            , publish=False
            )
    
        if form.validate_on_submit():

            session_id = models.generate_uuid()

            distance_meters = utilities.convert_distance_to_meters(form.distance_value.data, form.distance_units.data)

            local_timezone = models.get_location_timezone(location_id)

            new_session_object = models.ObservationSession(
                session_id=session_id
                , location_id=location_id
                , session_mode=form.session_mode.data
                , speed_limit_value=form.speed_limit_value.data
                , speed_units=form.speed_units.data
                , distance_meters=distance_meters
                , distance_value=form.distance_value.data
                , distance_units=form.distance_units.data
                , session_description=form.session_description.data
                , local_timezone=local_timezone
                , publish=form.publish.data
                )
            db.session.add(new_session_object)
            db.session.commit()

            if form.session_mode.data == 'speed timer':
                return redirect(f'session?session_id={session_id}')
            elif form.session_mode.data == 'counter':
                return redirect(f'counter?session_id={session_id}')

    else:
        # Existing session

        this_session = utilities.one_session(session_id)
        location_id = this_session['location_id']
        location_name = this_session['location_name']

        form = SessionSettingsForm(
            speed_limit_value=this_session['speed_limit_value']
            , speed_units=this_session['speed_units']
            , distance_value=this_session['distance_value']
            , distance_units=this_session['distance_units']
            , session_mode=this_session['session_mode']
            , session_description=this_session['session_description']
            , publish=this_session['publish']
            )

        if form.validate_on_submit():

            distance_meters = utilities.convert_distance_to_meters(form.distance_value.data, form.distance_units.data)

            with open(os.path.join(app.root_path, 'queries/sessions_update.sql'), 'r') as f:
                result = db.engine.execute(
                    text(f.read())
                    , session_id=session_id
                    , distance_meters=distance_meters
                    , distance_value=form.distance_value.data
                    , distance_units=form.distance_units.data
                    , speed_limit_value=form.speed_limit_value.data
                    , speed_units=form.speed_units.data
                    , session_mode=form.session_mode.data
                    , session_description=form.session_description.data
                    , publish=form.publish.data
                    , updated_at=utilities.now_utc()
                    )

            if form.session_mode.data == 'speed timer':
                return redirect(f'session?session_id={session_id}')
            elif form.session_mode.data == 'counter':
                return redirect(f'counter?session_id={session_id}&location_id={location_id}')

    
    return render_template(
        'session_settings.html'
        , form=form
        , location_id=location_id
        , location_name=location_name
        , session_id=session_id
        )



@socketio.on('connect')
@login_required
def new_socket_connection():
    """
    When a new user connects via websocket, assign them to a room based on the session_id
    """
    join_room(session['session_id'])



@socketio.on('broadcast start')
@login_required
def broadcast_start(message):
    """
    A new observation has been initiated
    """
    session_id = message['session_id']
    # location_id = message['location_id']

    # join_room(session_id)

    utc_time = utilities.now_utc()

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
@login_required
def broadcast_end(message):
    """
    The timer has ended for an observation
    """
    session_id = message['session_id']
    active_observation_id = message['active_observation_id']

    if active_observation_id == 'no_active_obs':
        print('No active observation ID passed')
        abort(500)

    utc_time = utilities.now_utc()

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



@app.route('/session', methods=['GET'])
@login_required
def session_handler():

    session_id = request.args.get('session_id')

    # A session_id needs to be provided to view this page
    if not session_id:
        abort(404)

    session['session_id'] = session_id

    this_session = utilities.one_session(session_id)

    with open(os.path.join(app.root_path, 'queries/observations_list.sql'), 'r') as f:
        observations = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

    completed_observations = observations[observations.end_time.notnull()].copy()

    

    if len(observations) == 0:

        vehicle_count = 0
        max_speed = 0
        median_speed = 0
        most_recent_speed = 0

    elif len(observations) == 1 and len(completed_observations) == 0:
        # first time through, timer_status = 'vehicle_in_timer'

        vehicle_count = 0
        max_speed = 0
        median_speed = 0
        most_recent_speed = 0

    else:

        completed_observations['speed_value'] = completed_observations.apply(
            lambda row: utilities.convert_speed_for_display(
                row.distance_meters
                , row.elapsed_seconds
                , row.speed_units
                )
            , axis=1
            )

        completed_observations = utilities.format_in_local_time(completed_observations, 'start_time', 'local_timezone', 'start_date_local', '%b %w, %Y')
        completed_observations = utilities.format_in_local_time(completed_observations, 'start_time', 'local_timezone', 'start_time_local', '%l:%M:%S %p')


        valid_observations = completed_observations[completed_observations.observation_valid].copy()
        vehicle_count = len(valid_observations)
        max_speed = valid_observations.speed_value.max()
        median_speed = valid_observations.speed_value.median()
        most_recent_speed = valid_observations['speed_value'].tolist()[0]
        
        speed_limit_value = observations.speed_limit_value.median()


    return render_template(
        'session.html'
        , session_id=session_id
        , location_id=this_session['location_id']
        , location_name=this_session['location_name']
        , vehicle_count=vehicle_count
        , max_speed=max_speed
        , median_speed=median_speed
        , most_recent_speed=most_recent_speed
        , speed_limit_value=this_session['speed_limit_value']
        , speed_units=this_session['speed_units']
        , distance_value=this_session['distance_value']
        , distance_units=this_session['distance_units']
        , qr=plot_qr_code()
        , this_url=request.url
        , df=completed_observations
        )



@app.route('/session/<session_id>/<observation_id>', methods=['POST'])
@login_required
def toggle_valid_on_list(session_id, observation_id):
    """
    When on a session page with a list of observations, toggle the validity of one observation
    """

    valid_action = request.args.get('valid_action')
    toggle_valid(observation_id, valid_action)

    return redirect(f'/session?session_id={session_id}')



@app.route('/session/<session_id>/plot.png')
@login_required
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

    session_observations['speed_value'] = session_observations.apply(
        lambda row: utilities.convert_speed_for_display(
            row.distance_meters
            , row.elapsed_seconds
            , row.speed_units
            )
        , axis=1
        )

    fig = Figure()
    fig.set_size_inches(4, 4)
    axis = fig.add_subplot(1, 1, 1)
    axis.hist(session_observations['speed_value'])

    axis.yaxis.set_major_locator(MaxNLocator(integer=True))
    axis.set_title('Histogram of Observed Speeds')
    axis.set_ylabel('Count of Vehicles')
    axis.set_xlabel(session_observations['speed_units'][0])

    return fig



def plot_qr_code():
    """
    Turn the request's URL into a QR code, so another user can join the observation session
    """

    qr = segno.make(request.url)
    return qr

