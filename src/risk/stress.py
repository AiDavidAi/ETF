import pandas as pd


def shock_pnl(positions: pd.Series, shocks: pd.Series) -> float:
    """Compute portfolio P&L under specified price shocks.

    Parameters
    ----------
    positions : pd.Series
        Position sizes in base currency per asset.
    shocks : pd.Series
        Price shocks expressed as returns for each asset.

    Returns
    -------
    float
        Aggregate P&L from applying ``shocks`` to ``positions``.
    """
    aligned = positions.reindex(shocks.index).fillna(0.0)
    return float((aligned * shocks).sum())
