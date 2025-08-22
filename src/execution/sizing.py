import pandas as pd
from typing import Union


def weights_to_contracts(
    weights: Union[pd.Series, pd.DataFrame],
    prices: Union[pd.Series, pd.DataFrame],
    multipliers: pd.Series,
    fx_rates: pd.Series,
    capital: float,
) -> pd.DataFrame:
    """Translate target portfolio weights into futures contract counts.

    Parameters
    ----------
    weights : Union[pd.Series, pd.DataFrame]
        Target portfolio weights for each asset.  May be a Series for a
        single timestamp or a DataFrame indexed by date.
    prices : Union[pd.Series, pd.DataFrame]
        Futures prices corresponding to ``weights``.  Must contain the same
        assets as columns/index.
    multipliers : pd.Series
        Contract multipliers for each asset.
    fx_rates : pd.Series
        FX rate of each asset's currency to the base portfolio currency.  The
        contract value is ``price * multiplier * fx``.
    capital : float
        Total portfolio value in base currency.

    Returns
    -------
    pd.DataFrame
        Number of contracts for each asset rounded to the nearest whole
        number.
    """

    if isinstance(weights, pd.Series):
        weights = weights.to_frame().T
    if isinstance(prices, pd.Series):
        prices = prices.to_frame().T

    if weights.empty:
        return pd.DataFrame(index=weights.index, columns=weights.columns)

    # Align multipliers and FX with columns
    multipliers = multipliers.reindex(weights.columns).astype(float)
    fx_rates = fx_rates.reindex(weights.columns).astype(float)

    notional = weights.astype(float) * float(capital)
    contract_value = prices.astype(float) * multipliers * fx_rates

    contracts = notional.div(contract_value)
    contracts = contracts.round().fillna(0).astype(int)
    return contracts
