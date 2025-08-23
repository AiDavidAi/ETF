import pandas as pd


def roll_weights(days_to_expiry: pd.Series, window: int) -> pd.Series:
    """Linear roll weights based on days to expiry.

    Parameters
    ----------
    days_to_expiry : pd.Series
        Days until the current contract expires for each asset.
    window : int
        Number of days over which to roll.  When ``days_to_expiry`` is greater
        than ``window`` no roll occurs.  At ``0`` days the roll is complete.

    Returns
    -------
    pd.Series
        Fraction of the position to allocate to the next contract (0 to 1).
    """
    if window <= 0:
        return pd.Series(0.0, index=days_to_expiry.index)
    frac = (window - days_to_expiry.astype(float)) / float(window)
    return frac.clip(lower=0.0, upper=1.0)
