
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response, abort
from flask_login import login_required, current_user

from . import db
from . import models
from . import utilities
from .forms import LocationSettingsForm



@app.route('/location_settings', methods=['GET', 'POST'])
@login_required
def edit_location_settings():
    """
    Receive information about each location
    """

    location_id = request.args.get('location_id')
    if not location_id:
        location_id = 'new_location'


    if location_id == 'new_location':
        # New location

        form = LocationSettingsForm(
            local_timezone='America/New_York'
            , city='Washington'
            , state_code='DC'
            )
    
        if form.validate_on_submit():

            location_id = models.generate_uuid()

            new_location_object = models.Location(
                location_id=location_id
                , location_name=form.location_name.data
                , street_address=form.street_address.data
                , city=form.city.data
                , state_code=form.state_code.data
                , zip_code=form.zip_code.data
                , location_description=form.location_description.data
                , local_timezone=form.local_timezone.data
                , managed_by_user_id=current_user.user_id
                , location_latitude=form.location_latitude.data
                , location_longitude=form.location_longitude.data
                )
            db.session.add(new_location_object)
            db.session.commit()

            return redirect(f'location?location_id={location_id}')

    else:
        # Existing location

        locations = utilities.one_location(location_id)

        form = LocationSettingsForm(
            location_name=locations['location_name']
            , local_timezone=locations['local_timezone']
            , street_address=locations['street_address']
            , city=locations['city']
            , state_code=locations['state_code']
            , zip_code=locations['zip_code']
            , location_description=locations['location_description']
            )

        if form.validate_on_submit():

            with open(os.path.join(app.root_path, 'queries/locations_update.sql'), 'r') as f:
                result = db.engine.execute(
                    text(f.read())
                    , location_id=location_id
                    , location_name=form.location_name.data
                    , local_timezone=form.local_timezone.data
                    , street_address=form.street_address.data
                    , city=form.city.data
                    , state_code=form.state_code.data
                    , zip_code=form.zip_code.data
                    , location_description=form.location_description.data
                    , updated_at=utilities.now_utc()
                    )

            return redirect(f'location?location_id={location_id}')


    return render_template(
        'location_settings.html'
        , form=form
        , location_id=location_id
        )


@app.route('/location_list', methods=['GET'])
def list_locations():
    """
    Display a list of all locations
    """

    if current_user.is_authenticated:
        this_user_sessions = utilities.list_of_user_sessions(current_user.user_id)
    else:
        this_user_sessions = []

    with open(os.path.join(app.root_path, 'queries/session_locations.sql'), 'r') as f:
        session_locations = pd.read_sql(text(f.read()), db.session.bind)

    session_locations_to_display = session_locations[(session_locations.publish) | (session_locations.session_id.isin(this_user_sessions))].copy()

    locations = session_locations_to_display.groupby('location_id').agg(
        num_sessions=('session_id', 'count')
        , num_speed_observations=('num_speed_observations', 'sum')
        , num_counter_observations=('num_counter_observations', 'sum')
        , most_recent_observation=('most_recent_observation', 'max')
        , local_timezone=('local_timezone', 'first')
        , city=('city', 'first')
        , state_code=('state_code', 'first')
        , location_name=('location_name', 'first')
        ).reset_index()


    locations = utilities.format_in_local_time(
        locations
        , 'most_recent_observation'
        , 'local_timezone'
        , 'most_recent_observation_local'
        , '%b %e, %Y %l:%M %p %Z'
        )

    locations['city_state'] = locations['city'] + ', ' + locations['state_code']

    locations = locations.sort_values(by='most_recent_observation', ascending=False)

    return render_template(
        'location_list.html'
        , locations=locations
        )



@app.route('/location', methods=['GET'])
def location_handler():

    location_id = request.args.get('location_id')

    # A location_id needs to be provided to view this page
    if not location_id:
        print('location_id not provided')
        abort(500)

    this_location = utilities.one_location(location_id)

    return render_template(
        'location.html'
        , location_id=location_id
        , location_name=this_location['location_name']
        , local_timezone=this_location['local_timezone']
        , street_address=this_location['street_address']
        , city=this_location['city']
        , state_code=this_location['state_code']
        , zip_code=this_location['zip_code']
        , location_description=this_location['location_description']
        , session_list_df=utilities.session_list_dataframe_for_display(location_id=location_id)
        )






