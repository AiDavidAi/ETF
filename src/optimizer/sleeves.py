from typing import Optional

import pandas as pd

from .erc import erc


def combine_sleeves(
    trend: pd.Series,
    carry: pd.Series,
    returns: Optional[pd.DataFrame] = None,
    method: str = "equal",
) -> pd.Series:
    """Combine trend and carry sleeves into a single portfolio.

    Parameters
    ----------
    trend, carry : pd.Series
        Asset weights from the respective sleeves. Index must align.
    returns : pd.DataFrame, optional
        Historical returns for the sleeves with columns ``['trend','carry']``.
        Required for ``method='risk_parity'``.
    method : str, default ``'equal'``
        ``'equal'`` averages the sleeves. ``'risk_parity'`` determines sleeve
        mix via equal risk contribution based on ``returns`` covariance.

    Returns
    -------
    pd.Series
        Combined asset weights.
    """
    trend = trend.fillna(0)
    carry = carry.fillna(0)
    if method == "equal" or returns is None:
        mix = pd.Series({"trend": 0.5, "carry": 0.5})
    elif method == "risk_parity":
        if returns is None or set(["trend", "carry"]) - set(returns.columns):
            raise ValueError("returns with 'trend' and 'carry' columns required")
        cov = returns[["trend", "carry"]].cov()
        mix = erc(cov)
        mix = mix / mix.sum()
    else:  # pragma: no cover - unknown method
        raise ValueError(f"unknown method: {method}")

    combined = mix["trend"] * trend + mix["carry"] * carry
    return combined
