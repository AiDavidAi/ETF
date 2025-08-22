import numpy as np
import pandas as pd


def volatility_scaled_momentum(
    prices: pd.DataFrame,
    lookback: int = 20,
    vol_lookback: int = 20,
) -> pd.DataFrame:
    """Compute volatility-scaled time-series momentum for each asset.

    Parameters
    ----------
    prices : pd.DataFrame
        Asset price data indexed by date with one column per asset.
    lookback : int, optional
        Number of periods to use for the momentum calculation.
    vol_lookback : int, optional
        Number of periods for estimating volatility. Defaults to ``lookback``
        when not provided.

    Returns
    -------
    pd.DataFrame
        DataFrame of the same shape as ``prices`` containing the
        volatility-scaled momentum signals.
    """

    if prices.empty:
        return pd.DataFrame(index=prices.index, columns=prices.columns)

    returns = prices.pct_change()
    momentum = prices.pct_change(lookback)
    volatility = returns.rolling(vol_lookback).std()

    signal = momentum / volatility
    signal = signal.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return signal
