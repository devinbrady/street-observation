
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import render_template, request, redirect

from . import db
from . import models
from . import utilities



@app.route('/counter', methods=['GET'])
def counter_handler():
    """
    Handle the GET on the counter page
    """

    session_id = request.args.get('session_id')
    this_session = utilities.one_session(session_id)

    with open(os.path.join(app.root_path, 'queries/emoji_list.sql'), 'r') as f:
        available_emoji = pd.read_sql(text(f.read()), db.session.bind)

    with open(os.path.join(app.root_path, 'queries/emoji_observations.sql'), 'r') as f:
        emoji_observations = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

    if len(emoji_observations) > 0:
        emoji_observations = utilities.format_in_local_time(emoji_observations, 'created_at', 'local_timezone', 'start_time_local', '%l:%M:%S %p')

        # Count the number of observations by the emoji that have been seen
        emoji_observation_count = (
            emoji_observations[emoji_observations.observation_valid]
            .groupby('emoji_id')
            .agg(num_observations=('counter_id', 'count'))
            .reset_index()
            )

        # Left join to the list of all emoji, to show zero for those not yet seen
        emoji_count = pd.merge(available_emoji, emoji_observation_count, how='left', on='emoji_id').sort_values(by='display_order')
        emoji_count['num_observations'] = emoji_count['num_observations'].fillna(0).astype(int)

        if len(emoji_observations) == 1:
            # Only one emoji has been observed, the session has no duration yet, so the per-hour calculation can't be done
            emoji_count['observations_per_hour'] = 0
            session_duration_hours = 0

        else:
            # Calculate the duration of this session so far
            earliest_time = emoji_observations['created_at'].min()
            latest_time = emoji_observations['created_at'].max()
            session_duration_hours = (latest_time - earliest_time).total_seconds() / 3600

            # Calculate the number of emoji per hour
            emoji_count['observations_per_hour'] = emoji_count['num_observations'] / session_duration_hours


    else:
        # Zero emoji have been observed

        emoji_count = available_emoji.copy()
        emoji_count['num_observations'] = 0
        emoji_count['observations_per_hour'] = 0
        session_duration_hours = 0

        emoji_observations = pd.DataFrame()


    return render_template(
        'counter.html'
        , emoji_count=emoji_count
        , emoji_observations=emoji_observations
        , session_id=session_id
        , location_id=this_session['location_id']
        , location_name=this_session['location_name']
        , session_duration_hours=session_duration_hours
        )



@app.route('/emoji', methods=['POST'])
def emoji_post():
    """
    Note the observation of a new emoji out on the street
    """

    session_id = request.args.get('session_id')
    location_id = request.args.get('location_id')
    emoji_id = request.args.get('emoji_id')

    local_timezone = models.get_location_timezone(location_id)
    
    new_counter_observation = models.CounterObservation(
        counter_id=models.generate_uuid()
        , session_id=session_id
        , location_id=location_id
        , emoji_id=int(emoji_id)
        , local_timezone=local_timezone
        )

    db.session.add(new_counter_observation)
    db.session.commit()

    return redirect(f'/counter?location_id={location_id}&session_id={session_id}')



@app.route('/emoji_validity', methods=['POST'])
def emoji_validity():
    """
    Handle the request to change the validity of an emoji observation
    """

    location_id = request.args.get('location_id')
    session_id = request.args.get('session_id')
    counter_id = request.args.get('counter_id')
    valid_action = request.args.get('valid_action')

    toggle_valid_counter(counter_id, valid_action)

    return redirect(f'/counter?location_id={location_id}&session_id={session_id}')



def toggle_valid_counter(counter_id, valid_action):
    """
    Change the validation status of a single emoji observation
    """

    with open(os.path.join(app.root_path, 'queries/emoji_observation_update.sql'), 'r') as f:

        result = db.engine.execute(
            text(f.read())
            , valid_action=valid_action
            , counter_id=counter_id
            , updated_at=utilities.now_utc()
            )
        
    # How to confirm this?
