"""
"""

import pandas as pd


def add_local_timestamps(df, local_tz):

    df['start_time_local'] = (
        df['start_time']
        .dt.tz_convert(local_tz)
        .dt.strftime('%l:%M:%S %p')
        )

    df['start_date_local'] = (
        df['start_time']
        .dt.tz_convert(local_tz)
        .dt.strftime('%b %w, %Y')
        )

    return df



def format_in_local_time(df, timestamp_column, tz_column, output_column, output_format):
    """
    Render a TZ-aware UTC column in a local timezone per the format specified
    """

    for idx, row in df.iterrows():
        df.loc[idx, output_column] = row[timestamp_column].astimezone(row[tz_column]).strftime(output_format)

    # df[output_column] = df.groupby(tz_column)[timestamp_column].transform(lambda x: x.dt.tz_convert(x.name))

    return df
