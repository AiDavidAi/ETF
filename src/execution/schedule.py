import numpy as np
import pandas as pd


def generate_cost_aware_schedule(quantity: float, costs: pd.Series) -> pd.DataFrame:
    """Allocate quantity across times based on estimated trading costs.

    Parameters
    ----------
    quantity : float
        Total quantity to trade.
    costs : pd.Series
        Estimated cost per slice indexed by execution time. Lower cost slices
        receive larger allocations.

    Returns
    -------
    pd.DataFrame
        Schedule with ``time`` and ``quantity`` columns.
    """
    if costs.empty:
        return pd.DataFrame(columns=["time", "quantity"])

    weights = 1.0 / costs.replace(0, np.nan)
    weights = weights.fillna(0)
    if weights.sum() == 0:
        weights = pd.Series(1.0 / len(costs), index=costs.index)
    else:
        weights = weights / weights.sum()
    qty = quantity * weights
    schedule = pd.DataFrame({"time": costs.index, "quantity": qty.values})
    return schedule
