
from flask import current_app as app
from flask import render_template
from geopy.distance import lonlat, distance
from flask_socketio import emit


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
    else:
        distance_meters = None

    emit(
        'info update'
        , {
            'user_a_latitude': user_a_latitude
            , 'user_a_longitude': user_a_longitude
            , 'user_b_latitude': user_b_latitude
            , 'user_b_longitude': user_b_longitude
            , 'distance_meters': distance_meters
        }
        , broadcast=True)



# @app.route('/distance', methods=['POST'])
# def post_distance():

#     print('hi')

#     form = DistanceForm()
#     if form.validate_on_submit():
#         print(form)

#     return render_template('distance.html', form=form)


@app.route('/locate_me', methods=['GET'])
def locate_me():
    
    return render_template('locate_me_2.html')
