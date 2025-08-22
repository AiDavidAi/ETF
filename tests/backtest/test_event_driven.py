import os
import sys
import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from backtest.event_driven import EventDrivenBacktester


def test_backtester_pnl():
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    prices = pd.DataFrame({"F1": [100, 101, 101], "F2": [102, 102, 103]}, index=dates)
    multipliers = pd.Series({"F1": 1.0, "F2": 1.0})
    bt = EventDrivenBacktester(prices, multipliers, slippage_bp=10)

    orders = {dates[0]: [("F1", 1)], dates[2]: [("F2", -1)]}
    rolls = {dates[1]: [("F1", "F2")]}

    portfolio = bt.run(orders, rolls)
    assert portfolio["value"].iloc[-1] == pytest.approx(1.594, rel=1e-3)
