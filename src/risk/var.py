import numpy as np
import pandas as pd
from typing import Union


def calculate_var(
    returns: Union[pd.Series, pd.DataFrame],
    confidence: float = 0.99,
    horizon: int = 20,
) -> Union[float, pd.Series]:
    """Historical Value-at-Risk using the square-root-of-time rule.

    Parameters
    ----------
    returns : Union[pd.Series, pd.DataFrame]
        Daily return series.  ``NaN`` values are ignored.
    confidence : float, optional
        Confidence level for VaR.  Default is ``0.99``.
    horizon : int, optional
        Number of days for VaR horizon.  Default is ``20``.

    Returns
    -------
    float or pd.Series
        VaR value(s) scaled to the requested horizon.  Positive numbers denote
        losses at the specified confidence level.
    """

    if isinstance(returns, pd.DataFrame):
        return returns.apply(
            lambda x: calculate_var(x, confidence=confidence, horizon=horizon)
        )

    if returns.empty:
        return float("nan")

    series = returns.dropna()
    if series.empty:
        return float("nan")

    quantile = np.nanquantile(series, 1 - confidence)
    var = -quantile * np.sqrt(horizon)
    return float(var)
