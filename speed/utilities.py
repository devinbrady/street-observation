"""
"""

import pandas as pd
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
