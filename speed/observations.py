"""
Routes related to a single observation
"""

import os
import pandas as pd
from sqlalchemy import text

from flask import current_app as app
from flask import request, render_template


from . import db
from . import utilities



@app.route('/observation/<observation_id>', methods=['GET', 'POST'])
def one_observation(observation_id):
    """
    Display information about one observation
    """

    if request.method == 'POST':
        valid_action = request.args.get('valid_action')
        toggle_valid(observation_id, valid_action)

    with open(os.path.join(app.root_path, 'queries/observations_one.sql'), 'r') as f:
        this_obs = pd.read_sql(text(f.read()), db.session.bind, params={'observation_id': observation_id})

    this_obs['speed_value'] = this_obs.apply(lambda row: utilities.convert_speed_for_display(
            row['distance_meters']
            , row['elapsed_seconds']
            , row['speed_units']
            )
        , axis=1
        )

    this_obs = utilities.format_in_local_time(this_obs, 'start_time', 'local_timezone', 'start_date_local', '%b %w, %Y')
    this_obs = utilities.format_in_local_time(this_obs, 'start_time', 'local_timezone', 'start_time_local', '%l:%M:%S %p')

    this_obs_series = this_obs.squeeze()

    return render_template(
        'observation.html'
        , observation_id=observation_id
        , session_id=this_obs_series['session_id']
        , location_id=this_obs_series['location_id']
        , start_date_local=this_obs_series['start_date_local']
        , start_time_local=this_obs_series['start_time_local']
        , distance_value=this_obs_series['distance_value']
        , distance_units=this_obs_series['distance_units']
        , elapsed_seconds=this_obs_series['elapsed_seconds']
        , speed_value=this_obs_series['speed_value']
        , speed_units=this_obs_series['speed_units']
        , speed_limit_value=this_obs_series['speed_limit_value']
        , observation_valid=this_obs_series['observation_valid']
        )



def toggle_valid(observation_id, valid_action):
    """
    Change the validation status of a single observation in the database
    """

    with open(os.path.join(app.root_path, 'queries/observations_update.sql'), 'r') as f:

        result = db.engine.execute(
            text(f.read())
            , valid_action=valid_action
            , observation_id=observation_id
            , updated_at=utilities.now_utc()
            )
        
    # How to confirm this?
