
from flask import current_app as app
from flask import render_template
from geopy.distance import lonlat, distance
from flask_socketio import emit
import pandas as pd
from sqlalchemy import text
import os

from . import db, socketio
from . import models
from . import utilities
from .forms import DistanceForm



@app.route('/distance', methods=['GET', 'POST'])
def get_distance():

    form = DistanceForm()

    if form.validate_on_submit():
        straight_line_meters = utilities.compute_distance(
            form.user_a_latitude.data
            , form.user_a_longitude.data
            , form.user_b_latitude.data
            , form.user_b_longitude.data
            )

    else:
        straight_line_meters = None
    
    return render_template('distance.html', form=form, straight_line_meters=straight_line_meters)



@socketio.on('geolocation reported')
def geolocation_reported(message):

    if 'user_a_latitude' in message:
        user_a_latitude = message['user_a_latitude']
    else:
        user_a_latitude = 0

    if 'user_a_longitude' in message:
        user_a_longitude = message['user_a_longitude']
    else:
        user_a_longitude = 0

    if 'user_b_latitude' in message:
        user_b_latitude = message['user_b_latitude']
    else:
        user_a_latitude = 0

    if 'user_b_longitude' in message:
        user_b_longitude = message['user_b_longitude']
    else:
        user_b_longitude = 0

    if user_a_latitude != 0 and user_b_latitude != 0 and user_b_latitude != 0 and user_b_latitude != 0:
        distance_meters = utilities.compute_distance(
            message['user_a_latitude']
            , message['user_a_longitude']
            , message['user_b_latitude']
            , message['user_b_longitude']
            )

        this_session = utilities.one_session(message['session_id'])
        distance_units = this_session['distance_units']
        distance_value = utilities.convert_meters_to_display_value(
            distance_meters
            , distance_units
            )

        distance_value_str = '{:0.1f}'.format(distance_value)

    else:
        distance_meters = -1
        distance_value_str = None
        distance_units = None

    emit(
        'info update'
        , {
            'user_a_latitude': user_a_latitude
            , 'user_a_longitude': user_a_longitude
            , 'user_b_latitude': user_b_latitude
            , 'user_b_longitude': user_b_longitude
            , 'distance_meters': distance_meters
            , 'distance_value': distance_value_str
            , 'distance_units': distance_units
        }
        , broadcast=True)



@socketio.on('use distance')
def geolocation_locked_in(message):

    this_session = utilities.one_session(message['session_id'])

    distance_value = utilities.convert_meters_to_display_value(
        message['distance_meters']
        , this_session['distance_units']
        )

    with open(os.path.join(app.root_path, 'queries/sessions_update_distance.sql'), 'r') as f:
        result = db.engine.execute(
            text(f.read())
            , session_id=message['session_id']
            , distance_meters=message['distance_meters']
            , distance_value=distance_value
            , updated_at=utilities.now_utc()
            )

    
