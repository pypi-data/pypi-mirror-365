from datetime import timedelta

import pandas as pd
from obspy import UTCDateTime


def hours(hour_ranges: pd.DatetimeIndex, period: int) -> list[dict]:
    """Get hours range list.

    Used to create IDDS filename.

    Args:
        hour_ranges: pd.DatetimeIndex
        period: int

    Returns:
        list[dict]: List of dict with 'index','start_hour' and 'end_hour'
    """
    _hours = []
    len_hours: int = len(str(len(hour_ranges)))

    for index, start_hour in enumerate(list(hour_ranges)):
        end_hour = start_hour + timedelta(minutes=period) - timedelta(milliseconds=1)
        _hours.append(
            {
                "index": str(index).zfill(len_hours),  # 001,002,...
                "start_hour": UTCDateTime(start_hour),
                "end_hour": UTCDateTime(end_hour),
            }
        )
    return _hours
