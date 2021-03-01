"""
"""

import pandas as pd


def add_local_timestamps(df, local_tz):

    df['start_time_local'] = (
        df['start_time']
        .dt.tz_localize('UTC')
        .dt.tz_convert(local_tz)
        .dt.strftime('%l:%M:%S %p')
        )

    df['start_date_local'] = (
        df['start_time']
        .dt.tz_localize('UTC')
        .dt.tz_convert(local_tz)
        .dt.strftime('%b %w, %Y')
        )

    return df
