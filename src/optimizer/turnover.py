import pandas as pd


def band_weights(
    target: pd.Series, current: pd.Series, band: float
) -> pd.Series:
    """Apply turnover banding to target weights.

    Parameters
    ----------
    target : pd.Series
        Desired portfolio weights.
    current : pd.Series
        Current portfolio weights.
    band : float
        No-trade band. Differences smaller than ``band`` are ignored.

    Returns
    -------
    pd.Series
        Adjusted weights after applying the turnover band.
    """
    data = pd.concat([target, current], axis=1, keys=["target", "current"]).fillna(0.0)
    diff = (data["target"] - data["current"]).abs()
    adjusted = data["target"].copy()
    within = diff <= band
    adjusted[within] = data.loc[within, "current"]
    return adjusted
