"""
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime, timezone



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

    if speed_units == 'miles_per_hour':
        return (distance_meters / 1609.34) / (elapsed_seconds / 3600)

    elif speed_units == 'kilometers_per_hour':
        return (distance_meters / 1000) / (elapsed_seconds / 3600)

    elif speed_units == 'meters_per_second':
        return distance_meters / elapsed_seconds

    elif speed_units == 'feet_per_second':
        return (distance_meters * 3.28084) / elapsed_seconds

    else:        
        print(f'Unknown units: {speed_units}')
        abort(500)



def display_speed_units(speed_units):

    return speed_units.replace('_', ' ')

