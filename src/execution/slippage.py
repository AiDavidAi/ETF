import numpy as np
import pandas as pd


def estimate_slippage(
    spread: pd.Series, volatility: pd.Series, participation: pd.Series, alpha: float = 0.1
) -> pd.Series:
    """Estimate implementation shortfall in basis points.

    cost = spread / 2 + alpha * volatility * sqrt(participation)
    All inputs are aligned by index.
    """
    spread = spread.reindex_like(volatility).fillna(0.0)
    participation = participation.reindex_like(volatility).fillna(0.0)
    cost = spread / 2.0 + alpha * volatility * np.sqrt(participation)
    return cost
