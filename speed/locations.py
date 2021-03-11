
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response, abort
from flask_login import login_required

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
@login_required
def list_locations():
    """
    Display a list of all locations
    """

    with open(os.path.join(app.root_path, 'queries/locations_list.sql'), 'r') as f:
        locations = pd.read_sql(f.read(), db.session.bind)

    locations = utilities.format_in_local_time(
        locations
        , 'most_recent_observation'
        , 'local_timezone'
        , 'most_recent_observation_local'
        , '%Y-%m-%d %l:%M %p %Z'
        )

    locations['city_state'] = locations['city'] + ', ' + locations['state_code']

    return render_template(
        'location_list.html'
        , locations=locations
        )



@app.route('/location', methods=['GET'])
@login_required
def location_handler():

    location_id = request.args.get('location_id')

    # A location_id needs to be provided to view this page
    if not location_id:
        abort(404)

    this_location = utilities.one_location(location_id)


    # Speed observation sessions that have occurred at this location
    with open(os.path.join(app.root_path, 'queries/observations_at_location.sql'), 'r') as f:
        obs = pd.read_sql(text(f.read()), db.session.bind, params={'location_id': location_id})

    if len(obs) == 0:
        sessions_at_location = pd.DataFrame()
    else:
        obs['speed_value'] = obs.apply(
            lambda row: utilities.convert_speed_for_display(
                row.distance_meters
                , row.elapsed_seconds
                , row.speed_units
                )
            , axis=1
            )
       
        sessions_at_location = obs.groupby('session_id').agg(
            session_id=('session_id', 'first')
            , start_timestamp_min=('start_time', 'min')
            , start_timestamp_max=('start_time', 'max')
            , local_timezone=('local_timezone', 'first')
            , session_description=('session_description', 'first')
            , distance_value=('distance_value', 'median')
            , distance_units=('distance_units', 'first')
            , median_speed=('speed_value', 'median')
            , num_observations=('observation_id', 'count')
            )

        sessions_at_location['session_duration_minutes'] = (sessions_at_location['start_timestamp_max'] - sessions_at_location['start_timestamp_min']).dt.total_seconds() / 60
        sessions_at_location = utilities.format_in_local_time(sessions_at_location, 'start_timestamp_min', 'local_timezone', 'start_timestamp_local', '%Y-%m-%d %l:%M %p %Z')
        sessions_at_location = sessions_at_location.sort_values(by='start_timestamp_min', ascending=False)
        


    # Counter sessions that have occurred at this location
    with open(os.path.join(app.root_path, 'queries/counter_observations_at_location.sql'), 'r') as f:
        counter_obs = pd.read_sql(text(f.read()), db.session.bind, params={'location_id': location_id})

    if len(counter_obs) == 0:
        counter_sessions_at_location = pd.DataFrame()
    else:

        # Within each session, rank emoji by the number of observations. Break ties with display_order (pedestrians first, trucks last)
        emoji_by_session = counter_obs.groupby(['session_id', 'glyph']).agg(
            num_observations=('counter_id', 'count')
            , display_order=('display_order', 'first')
            ).sort_values(by=['session_id', 'display_order'])
        emoji_by_session_rank = emoji_by_session.groupby('session_id')['num_observations'].rank(method='first', ascending=False)
        emoji_by_session_rank.name = 'emoji_rank'
        df = pd.DataFrame(emoji_by_session_rank[emoji_by_session_rank <= 3]).reset_index().sort_values(by=['session_id', 'emoji_rank'])
        common_emoji_df = df.groupby('session_id')['glyph'].apply(', '.join).reset_index()
        common_emoji_df = common_emoji_df.rename(columns={'glyph': 'most_common_emoji'})

        # Calculate other stats about each counter observation session
        counter_sessions_at_location = counter_obs.groupby('session_id').agg(
            created_at_min=('created_at', 'min')
            , created_at_max=('created_at', 'max')
            , local_timezone=('local_timezone', 'first')
            , session_description=('session_description', 'first')
            , num_observations=('counter_id', 'count')
            ).reset_index()

        counter_sessions_at_location = pd.merge(counter_sessions_at_location, common_emoji_df, how='inner', on='session_id')

        counter_sessions_at_location['session_duration_minutes'] = (counter_sessions_at_location['created_at_max'] - counter_sessions_at_location['created_at_min']).dt.total_seconds() / 60
        counter_sessions_at_location = utilities.format_in_local_time(counter_sessions_at_location, 'created_at_min', 'local_timezone', 'start_timestamp_local', '%Y-%m-%d %l:%M %p %Z')
        counter_sessions_at_location = counter_sessions_at_location.sort_values(by='created_at_min', ascending=False)


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
        , sessions_at_location=sessions_at_location
        , counter_sessions_at_location=counter_sessions_at_location
        )






