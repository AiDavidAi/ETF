import pandas as pd
from typing import Union


def forecast_margin(
    notional: pd.Series, margin_rates: Union[pd.Series, float]
) -> pd.Series:
    """Estimate margin requirements for a set of positions.

    Parameters
    ----------
    notional : pd.Series
        Notional exposure of each position in base currency.
    margin_rates : Union[pd.Series, float]
        Initial margin rates as a fraction of notional.  Can be a scalar or a
        Series indexed like ``notional``.

    Returns
    -------
    pd.Series
        Required margin per position.
    """
    if isinstance(margin_rates, (int, float)):
        rates = pd.Series(margin_rates, index=notional.index, dtype=float)
    else:
        rates = margin_rates.reindex(notional.index).astype(float).fillna(0.0)
    return notional.abs().astype(float) * rates
