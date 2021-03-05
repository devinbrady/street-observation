"""
"""

import os
import pandas as pd
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime, timezone
from flask import current_app as app

from . import db


def format_in_local_time(df, timestamp_column, tz_column, output_column, output_format):
    """
    Render a TZ-aware UTC column in a local timezone per the format specified
    """

    for idx, row in df.iterrows():
        df.loc[idx, output_column] = row[timestamp_column].astimezone(row[tz_column]).strftime(output_format)

    # df[output_column] = df.groupby(tz_column)[timestamp_column].transform(lambda x: x.dt.tz_convert(x.name))

    return df



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



def convert_speed_for_display(distance_meters, elapsed_seconds, speed_units):

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



def display_speed_units(speed_units):

    return speed_units.replace('_', ' ')



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
