import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from risk import forecast_margin, shock_pnl


def test_forecast_margin_and_stress():
    notional = pd.Series({"A": 100000, "B": -50000})
    rates = pd.Series({"A": 0.1, "B": 0.2})
    margin = forecast_margin(notional, rates)
    assert margin["A"] == pytest.approx(10000)
    assert margin["B"] == pytest.approx(10000)
    shocks = pd.Series({"A": -0.05, "B": 0.1})
    pnl = shock_pnl(notional, shocks)
    # A loses 5k, B loses -5k? Wait: notional -50000 * shock 0.1 -> -5000; sum -10000
    assert pnl == pytest.approx(-10000)
