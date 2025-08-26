from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from .roll import roll_weights
from .schedule import generate_cost_aware_schedule
from .sizing import weights_to_contracts
from .slippage import estimate_slippage


def plan_orders(
    target_weights: pd.Series,
    current_positions: pd.Series,
    market_data: Dict[str, pd.Series],
    roll_window: int = 5,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Create executable order schedules and estimate their costs.

    Parameters
    ----------
    target_weights : pd.Series
        Desired portfolio weights by asset.
    current_positions : pd.Series
        Current contract holdings for each asset.
    market_data : dict
        Dictionary containing market inputs. Required keys are ``prices``,
        ``multipliers``, ``fx_rates``, ``capital``, ``spread``, ``volatility``,
        ``volume``, ``costs``, and ``days_to_expiry``.
    roll_window : int, optional
        Window in days over which to roll expiring contracts.

    Returns
    -------
    tuple
        ``(schedule, costs)`` where ``schedule`` is a DataFrame with columns
        ``asset``, ``time``, and ``quantity`` and ``costs`` is a Series of
        expected slippage cost per asset.

    Examples
    --------
    >>> schedule, cost = plan_orders(target_weights, positions, data)
    >>> schedule.head()
    """
    prices = market_data["prices"]
    multipliers = market_data["multipliers"]
    fx_rates = market_data["fx_rates"]
    capital = float(market_data.get("capital", 0.0))

    target_contracts = weights_to_contracts(
        target_weights, prices, multipliers, fx_rates, capital
    ).iloc[0]

    current_positions = current_positions.reindex(target_contracts.index).fillna(0.0)

    trade_contracts = target_contracts - current_positions

    roll_frac = roll_weights(market_data["days_to_expiry"], roll_window)
    roll_qty = current_positions * roll_frac

    total_trade = trade_contracts + roll_qty

    volume = market_data["volume"].reindex(target_contracts.index).fillna(1.0)
    participation = (total_trade.abs() / volume).fillna(0.0)

    spreads = market_data["spread"].reindex(target_contracts.index)
    volatility = market_data["volatility"].reindex(target_contracts.index)
    slippage = estimate_slippage(spreads, volatility, participation)
    expected_cost = (slippage * total_trade.abs()).rename("cost")

    schedules = []
    costs_curve = market_data["costs"]
    for asset, qty in total_trade.items():
        if qty == 0:
            continue
        sched = generate_cost_aware_schedule(float(qty), costs_curve)
        sched["asset"] = asset
        schedules.append(sched)

    if schedules:
        schedule_df = pd.concat(schedules, ignore_index=True)[
            ["asset", "time", "quantity"]
        ]
    else:
        schedule_df = pd.DataFrame(columns=["asset", "time", "quantity"])

    return schedule_df, expected_cost
