"""
"""

import os
import numpy as np
import pandas as pd
from sqlalchemy import text, bindparam
from decimal import Decimal
from dateutil import tz
from datetime import datetime, timezone
from geopy.distance import lonlat, distance

from flask import current_app as app
from flask_login import current_user

from . import db
from . import models



def compute_distance(lat_a, lon_a, lat_b, lon_b):
    """
    Return float with distance between two points in meters
    """

    return distance((lat_a, lon_a), (lat_b, lon_b)).meters



def session_permissions(this_session):
    """
    Returns booleans to show whether this session can be viewe, added to, and edited by the current user
    """

    # Default to not allowing new observations to be collected or the page to be viewed
    allow_session_view = False
    allow_data_entry = False
    allow_session_edit = False

    is_session_recent = session_recency(this_session['created_at'].to_pydatetime())

    if is_session_recent:

        if current_user.is_authenticated:
            # When the session is less than 24 hours old, any logged-in user with the link can add observations
            allow_session_view = True
            allow_data_entry = True
            allow_session_edit = True


        elif this_session['publish']:
            # When the session is less than 24 hours old and the session is published, anyone can view the page but not add data
            allow_session_view = True
            allow_data_entry = False
            allow_session_edit = False

        else:
            # When the session is less than 24 hours old, the session is NOT published, and the user is NOT logged in, the user can't see this page
            allow_session_view = False
            allow_data_entry = False
            allow_session_edit = False


    else:
        # The session is more than 24 hours old, don't allow anyone to add more data
        allow_data_entry = False

        if this_session['publish']:
            # It's a published session, anyone can view it
            allow_session_view = True

        else:

            # When the session is more than 24 hours old, the session is not published, and the user is logged in, the user must have the ability to see the session
            if current_user.is_authenticated:
                this_user_sessions = list_of_user_sessions(current_user.user_id)
            else:
                this_user_sessions = []

            if this_session['session_id'] in this_user_sessions:
                allow_session_view = True
                allow_session_edit = True
            else:
                allow_session_view = False
                allow_session_edit = False

    return allow_session_view, allow_data_entry, allow_session_edit



def session_list_dataframe_for_display(location_id=None):
    """
    Return dataframe containing the sessions of all modes that the current user is entitled to see
    """

    with open(os.path.join(app.root_path, 'queries/session_list.sql'), 'r') as f:
        all_sessions_df = pd.read_sql(text(f.read()), db.session.bind)

    # If a location_id is provided, narrow sessions to those that occur at the location
    if location_id:
        all_sessions_df = all_sessions_df[all_sessions_df['location_id'] == location_id].copy()

    if current_user.is_authenticated:
        this_user_sessions = list_of_user_sessions(current_user.user_id)
    else:
        this_user_sessions = []

    # Only display published sessions and private sessions connected to this user
    session_list_df = all_sessions_df[(all_sessions_df.publish) | (all_sessions_df.session_id.isin(this_user_sessions))].copy()

    if len(session_list_df) > 0:

        session_list_df = format_in_local_time(
            session_list_df, 'created_at', 'local_timezone', 'created_at_local', '%b %e, %Y %l:%M %p %Z')

        columns_to_union = ['session_id', 'num_observations', 'result']


        # Calculate stats about the speed timer sessions on this list
        speed_timer_sessions = session_list_df[session_list_df.session_mode == 'speed timer']['session_id'].tolist()

        if len(speed_timer_sessions) == 0:
            timer_sessions = pd.DataFrame(columns=columns_to_union)
        else:

            with open(os.path.join(app.root_path, 'queries/observations_speed_timer_session_list.sql'), 'r') as f:
                timer_obs = pd.read_sql(
                    text(f.read()).bindparams(bindparam('speed_timer_sessions', expanding=True))
                    , db.session.bind
                    , params={'speed_timer_sessions': speed_timer_sessions}
                    )

            if len(timer_obs) == 0:
                timer_sessions = pd.DataFrame(columns=columns_to_union)
            else:
                # todo: this is to cover for a bug, not sure why it's happening, should eventually be removed
                timer_obs['speed_value'] = timer_obs.apply(
                    lambda row: convert_to_speed_units(
                        row.distance_meters
                        , row.elapsed_seconds
                        , row.speed_units
                        )
                    , axis=1
                )

                timer_sessions = timer_obs.groupby('session_id').agg(
                    start_timestamp_min=('start_time', 'min')
                    , start_timestamp_max=('start_time', 'max')
                    , local_timezone=('local_timezone', 'first')
                    , speed_units=('speed_units', 'first')
                    , median_speed=('speed_value', 'median')
                    , num_observations=('observation_id', 'count')
                ).reset_index()

                timer_sessions['speed_units_short'] = timer_sessions['speed_units'].map(abbreviate_speed_units())
                timer_sessions['result'] = timer_sessions.apply(
                    lambda row: f"Median speed: {row['median_speed']:.1f} {row['speed_units_short']}"
                    , axis=1)


        # Calculate stats about the speed timer sessions on this list
        counter_sessions = session_list_df[session_list_df.session_mode == 'counter']['session_id'].tolist()

        if len(counter_sessions) == 0:
            counter_sessions = pd.DataFrame(columns=columns_to_union)
        else:

            with open(os.path.join(app.root_path, 'queries/observations_counter_session_list.sql'), 'r') as f:
                counter_obs = pd.read_sql(
                    text(f.read()).bindparams(bindparam('counter_sessions', expanding=True))
                    , db.session.bind
                    , params={'counter_sessions': counter_sessions}
                    )

            # Within each session, rank emoji by the number of observations. Break ties with display_order (pedestrians first, trucks last)
            emoji_by_session = counter_obs.groupby(['session_id', 'glyph']).agg(
                num_observations=('counter_id', 'count')
                , display_order=('display_order', 'first')
                ).sort_values(by=['session_id', 'display_order'])
            emoji_by_session_rank = emoji_by_session.groupby('session_id')['num_observations'].rank(method='first', ascending=False)
            emoji_by_session_rank.name = 'emoji_rank'
            df = pd.DataFrame(emoji_by_session_rank[emoji_by_session_rank <= 3]).reset_index().sort_values(by=['session_id', 'emoji_rank'])
            common_emoji_df = 'Most common: ' + df.groupby('session_id')['glyph'].apply(', '.join)
            common_emoji_df.name = 'result'

            counter_num_obs = counter_obs.groupby('session_id').size()
            counter_num_obs.name = 'num_observations'

            counter_sessions = pd.merge(counter_num_obs, common_emoji_df, how='inner', left_index=True, right_index=True).reset_index()

        # Combine timer and counter sessions
        union_modes = pd.concat([timer_sessions[columns_to_union], counter_sessions[columns_to_union]])
        session_list_df = pd.merge(session_list_df, union_modes, how='inner', on='session_id')

    session_list_df = session_list_df.sort_values(by='created_at', ascending=False)

    return session_list_df



def list_of_user_sessions(user_id):
    """
    Return a list of session_ids that the user is able to see
    """

    if current_user.username == 'admin':
        # Admin user is shown all sessions
        with open(os.path.join(app.root_path, 'queries/user_sessions_all.sql'), 'r') as f:
            user_sessions_df = pd.read_sql(text(f.read()), db.session.bind)

    else:
        with open(os.path.join(app.root_path, 'queries/user_sessions.sql'), 'r') as f:
            user_sessions_df = pd.read_sql(text(f.read()), db.session.bind, params={'user_id': current_user.user_id})

    return user_sessions_df['session_id'].tolist()



def session_recency(created_at):
    """
    If a session is more than 24 hours old, do not allow new observations to be added
    """

    age_of_session = now_utc() - created_at

    if age_of_session.days == 0:
        session_time_valid = True
    else:
        session_time_valid = False

    return session_time_valid



def hour_minute_string(total_seconds):
    """
    Convert a float number of seconds to a string spelling out the hours and minutes
    """

    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    hours_floor = np.floor(total_hours)
    minutes_remainder = total_minutes % 60

    if hours_floor > 0:
        duration_string = f'{hours_floor:.0f} hour{"s" if hours_floor > 1 else ""} and '
    else:
        duration_string = ''

    duration_string += f'{minutes_remainder:.0f} minute{"s" if minutes_remainder >= 1.5 else ""}'

    return duration_string



def format_in_local_time(df, timestamp_column, tz_column, output_column, output_format):
    """
    Render a TZ-aware UTC column in a local timezone per the format specified
    """

    # Default output value is an empty string
    df[output_column] = ''

    # Convert timezone for non-null timestamps
    for idx, row in df[df[timestamp_column].notnull()].iterrows():

        local_tz = tz.gettz(row[tz_column])
        df.loc[idx, output_column] = row[timestamp_column].astimezone(local_tz).strftime(output_format)

    # df[output_column] = df.groupby(tz_column)[timestamp_column].transform(lambda x: x.dt.tz_convert(x.name))

    return df



def convert_timestamp_to_local_time(timestamp_utc, local_timezone, output_format):

    local_tz = tz.gettz(local_timezone)
    return timestamp_utc.astimezone(local_tz).strftime(output_format)



def now_utc():
    """
    Return the current time according to the server, localized to UTC
    """

    return datetime.now(tz=timezone.utc)



def convert_distance_to_meters(value, unit):
    """
    Return a distance value in meters
    """

    if unit == 'feet':
        return value * Decimal(0.3048)

    elif unit == 'miles':
        return value * Decimal(1609.34)

    elif unit == 'meters':
        return value

    elif unit == 'kilometers':
        return value * Decimal(1000)

    else:
        print(f'Unknown units: {unit}')
        abort(500)



def convert_meters_to_display_value(distance_meters, unit):
    """
    Return a distance value for display
    """

    distance_meters_dec = Decimal(distance_meters)

    if unit == 'feet':
        return distance_meters_dec / Decimal(0.3048)

    elif unit == 'miles':
        return distance_meters_dec / Decimal(1609.34)

    elif unit == 'meters':
        return distance_meters_dec

    elif unit == 'kilometers':
        return distance_meters_dec / Decimal(1000)

    else:
        print(f'Unknown units: {unit}')
        abort(500)



def convert_to_speed_units(distance_meters, elapsed_seconds, speed_units):
    """
    Convert the speed, always stored in meters and seconds, to the specified speed_units
    """

    if speed_units == 'miles per hour':
        return (distance_meters / 1609.34) / (elapsed_seconds / 3600)

    elif speed_units == 'kilometers per hour':
        return (distance_meters / 1000) / (elapsed_seconds / 3600)

    elif speed_units == 'meters per second':
        return distance_meters / elapsed_seconds

    elif speed_units == 'feet per second':
        return (distance_meters * 3.28084) / elapsed_seconds

    else:        
        print(f'Unknown units: {speed_units}')
        abort(500)



def abbreviate_speed_units():
    """
    Return dictionary with abbreviation for speed units, for Series.map() usage
    """

    return {
        'miles per hour': 'mph'
        , 'kilometers per hour': 'kph'
        , 'meters per second': 'm per sec'
        , 'feet per second': 'ft per sec'
    }



def one_location(location_id):
    """
    Return dataframe containing information about one location
    """

    with open(os.path.join(app.root_path, 'queries/locations_one.sql'), 'r') as f:
        locations_df = pd.read_sql(text(f.read()), db.session.bind, params={'location_id': location_id})
        this_location = locations_df.squeeze()

    return this_location



def one_session(session_id):
    """
    Return dataframe containing information about one session
    """

    with open(os.path.join(app.root_path, 'queries/sessions_one.sql'), 'r') as f:
        session_df = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})
        this_session = session_df.squeeze()

    return this_session



def user_session_exists(user_id, session_id):
    """
    Return dataframe containing information about one user_session
    """

    with open(os.path.join(app.root_path, 'queries/user_sessions_one.sql'), 'r') as f:
        user_session_df = pd.read_sql(text(f.read()), db.session.bind, params={'user_id': user_id, 'session_id': session_id})
    
    if len(user_session_df) > 1:
        print('Duplicate entries in user_sessions')
        abort(500)

    return len(user_session_df) == 1



def activate_user_session(session_id, local_timezone):
    """
    Insert a new row in the user_sessions table connecting this user to this session, if it hasn't already been done
    """

    if not user_session_exists(current_user.user_id, session_id):

        new_user_session_object = models.UserSession(
            user_id=current_user.user_id
            , session_id=session_id
            , local_timezone=local_timezone
            )
        db.session.add(new_user_session_object)
        db.session.commit()

    return
