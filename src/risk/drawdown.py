import numpy as np
import pandas as pd


def scale_by_drawdown(equity_curve: pd.Series, max_drawdown: float) -> float:
    """Scale exposure based on trailing drawdown.

    Parameters
    ----------
    equity_curve : pd.Series
        Series of cumulative portfolio values.
    max_drawdown : float
        Drawdown level at which exposure is fully reduced.

    Returns
    -------
    float
        Scaling factor between ``0`` and ``1``.  Returns ``1`` when there is
        no drawdown.
    """
    if max_drawdown <= 0:
        raise ValueError("max_drawdown must be positive")
    if equity_curve.empty:
        return 1.0

    peak = equity_curve.cummax()
    drawdown = (peak - equity_curve) / peak
    current = drawdown.iloc[-1]
    scale = 1 - current / max_drawdown
    return float(np.clip(scale, 0.0, 1.0))
