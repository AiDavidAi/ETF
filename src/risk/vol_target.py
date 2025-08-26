import numpy as np
import pandas as pd


def scale_to_target_vol(
    returns: pd.Series, target_vol: float, window: int = 252
) -> float:
    """Leverage multiplier to hit a target volatility.

    Parameters
    ----------
    returns : pd.Series
        Daily return series.
    target_vol : float
        Desired annualized volatility (e.g., ``0.1`` for 10%).
    window : int, optional
        Lookback window for realized volatility.  Default is ``252``.

    Returns
    -------
    float
        Multiplier to scale positions.  Returns ``0`` if volatility is
        ``0`` or cannot be estimated.
    """
    if window <= 0:
        raise ValueError("window must be positive")

    series = returns.dropna().tail(window)
    if series.empty:
        return 0.0

    realized = series.std(ddof=0) * np.sqrt(252)
    if not np.isfinite(realized) or realized == 0:
        return 0.0

    return float(target_vol / realized)
