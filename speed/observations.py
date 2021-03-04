"""
Routes related to a single observation
"""

import os
import pandas as pd
from sqlalchemy import text

from flask import current_app as app
from flask import request, render_template


from . import db
from . import dataframes



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

    this_obs['mph'] = this_obs['distance_miles'] / (this_obs['elapsed_seconds'] / 60 / 60)

    this_obs = dataframes.format_in_local_time(this_obs, 'start_time', 'local_timezone', 'start_date_local', '%b %w, %Y')
    this_obs = dataframes.format_in_local_time(this_obs, 'start_time', 'local_timezone', 'start_time_local', '%l:%M:%S %p')

    this_obs_series = this_obs.squeeze()

    return render_template(
        'observation.html'
        , observation_id=observation_id
        , session_id=this_obs_series['session_id']
        , location_id=this_obs_series['location_id']
        , start_date_local=this_obs_series['start_date_local']
        , start_time_local=this_obs_series['start_time_local']
        , distance_miles=this_obs_series['distance_miles']
        , elapsed_seconds=this_obs_series['elapsed_seconds']
        , mph=this_obs_series['mph']
        , speed_limit_mph=this_obs_series['speed_limit_mph']
        , observation_valid=this_obs_series['observation_valid']
        )



def toggle_valid(observation_id, valid_action):
    """
    Change the validation status of a single observation in the database
    """

    update_query = text('''
        update observations
        set observation_valid = :valid_action
        where observation_id = :observation_id
    ''')

    result = db.engine.execute(
        update_query
        , valid_action=valid_action
        , observation_id=observation_id
        )
    # How to confirm this?
