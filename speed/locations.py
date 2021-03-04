
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import session, redirect, url_for, request, render_template, send_from_directory, Response, abort

from . import models
from . import db
from .forms import LocationSettingsForm


@app.route('/location_settings', methods=['GET', 'POST'])
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
                location_id
                , form.location_name.data
                , form.local_timezone.data
                , form.street_address.data
                , form.city.data
                , form.state_code.data
                , form.zip_code.data
                , form.location_description.data
                )
            db.session.add(new_location_object)
            db.session.commit()

            session['local_timezone'] = form.local_timezone.data

            return redirect(f'session_settings?session_id=new_session&location_id={location_id}')

    else:
        # Existing location

        with open(os.path.join(app.root_path, 'queries/locations_one.sql'), 'r') as f:
            locations_df = pd.read_sql(text(f.read()), db.session.bind, params={'location_id': location_id})

        locations = locations_df.squeeze()

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
                    )

            session['local_timezone'] = form.local_timezone.data

            return redirect(f'location_settings?location_id={location_id}')


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

    with open(os.path.join(app.root_path, 'queries/locations_list.sql'), 'r') as f:
        locations = pd.read_sql(f.read(), db.session.bind)

    # locations['start_timestamp_local'] = (
    #     locations['first_start']
    #     .dt.tz_localize('UTC')
    #     .dt.tz_convert(locations['local_timezone'])
    #     .dt.strftime('%Y-%m-%d %l:%M:%S %p')
    #     )


    return render_template(
        'location_list.html'
        , locations=locations
        )