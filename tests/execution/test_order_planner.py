import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import plan_orders


def test_plan_orders_end_to_end():
    target_weights = pd.Series({"ES": 0.1})
    current_positions = pd.Series({"ES": 10})
    costs = pd.Series(
        [1.0, 2.0], index=pd.date_range("2021-01-01 09:30", periods=2, freq="H")
    )
    market_data = {
        "prices": pd.Series({"ES": 100.0}),
        "multipliers": pd.Series({"ES": 10.0}),
        "fx_rates": pd.Series({"ES": 1.0}),
        "capital": 100_000.0,
        "spread": pd.Series({"ES": 1.0}),
        "volatility": pd.Series({"ES": 0.02}),
        "volume": pd.Series({"ES": 1000}),
        "costs": costs,
        "days_to_expiry": pd.Series({"ES": 2}),
    }

    schedule, costs_series = plan_orders(
        target_weights, current_positions, market_data, roll_window=4
    )

    assert schedule["quantity"].sum() == pytest.approx(5.0)
    assert len(schedule) == 2
    assert schedule["asset"].unique().tolist() == ["ES"]
    expected_cost = 0.5001414213562373 * 5.0
    assert costs_series["ES"] == pytest.approx(expected_cost)
