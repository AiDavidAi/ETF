import pandas as pd
from typing import Union


def generate_twap_schedule(
    quantity: float,
    start: Union[pd.Timestamp, str],
    end: Union[pd.Timestamp, str],
    slices: int,
) -> pd.DataFrame:
    """Split an order into a simple time-weighted schedule.

    Parameters
    ----------
    quantity : float
        Total quantity to trade.  Positive for buy, negative for sell.
    start : Union[pd.Timestamp, str]
        Start time of the schedule.
    end : Union[pd.Timestamp, str]
        End time of the schedule.
    slices : int
        Number of child orders to create.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``time`` and ``quantity`` representing the
        schedule.  Quantities are evenly split and times are evenly spaced
        between ``start`` and ``end`` inclusive.
    """

    if slices <= 0:
        return pd.DataFrame(columns=["time", "quantity"])

    start_ts = pd.to_datetime(start)
    end_ts = pd.to_datetime(end)

    times = pd.date_range(start_ts, end_ts, periods=slices)
    qty = quantity / float(slices)
    schedule = pd.DataFrame({"time": times, "quantity": qty})
    return schedule
