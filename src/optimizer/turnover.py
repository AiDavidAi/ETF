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


def penalized_band_weights(
    target: pd.Series, current: pd.Series, band: float, penalty: float
) -> pd.Series:
    """Apply banding and shrink adjustments to reduce turnover.

    Parameters
    ----------
    target : pd.Series
        Desired portfolio weights.
    current : pd.Series
        Current portfolio weights.
    band : float
        No-trade band. Differences smaller than ``band`` are ignored.
    penalty : float
        Fraction [0, 1] of the trade to penalize.  ``0`` executes fully towards
        ``target``; ``1`` leaves ``current`` unchanged.

    Returns
    -------
    pd.Series
        Adjusted weights after banding and penalization.
    """

    banded = band_weights(target, current, band)
    diff = banded - current
    adjusted = current + diff * (1 - float(penalty))
    return adjusted
