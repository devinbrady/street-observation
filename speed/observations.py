"""
Routes related to a single observation
"""

import pandas as pd
from sqlalchemy import text

from flask import current_app as app
from flask import request, render_template


from . import db
from . import dataframes


local_timezone = 'America/New_York'


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
        , o.observation_valid
        , s.session_id
        , s.distance_miles
        , s.speed_limit_mph
        , s.location_id

        from observations o
        inner join sessions s using (session_id)

        where o.observation_id = '{observation_id}'
        '''
        , db.session.bind
        )

    this_obs['mph'] = this_obs['distance_miles'] / (this_obs['elapsed_seconds'] / 60 / 60)

    this_obs = dataframes.add_local_timestamps(this_obs, local_tz=local_timezone)

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
