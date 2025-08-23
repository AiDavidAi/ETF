import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from signals import equity_carry, bond_carry, commodity_carry, fx_carry


def test_equity_carry_standardization():
    idx = pd.date_range("2020-01-01", periods=2)
    dividend = pd.DataFrame({"A": [0.03, 0.02], "B": [0.01, 0.015]}, index=idx)
    financing = 0.01
    signals = equity_carry(dividend, financing)
    last = signals.iloc[-1]
    assert last["A"] > 0
    assert last["B"] < 0
    assert signals.mean(axis=1).iloc[-1] == pytest.approx(0.0)
    assert signals.std(axis=1).iloc[-1] == pytest.approx(1.0)


def test_bond_carry_standardization():
    idx = pd.date_range("2020-01-01", periods=1)
    yld = pd.DataFrame({"A": [0.02], "B": [0.03]}, index=idx)
    roll = pd.DataFrame({"A": [0.005], "B": [0.002]}, index=idx)
    signals = bond_carry(yld, roll)
    row = signals.iloc[0]
    assert row["B"] > row["A"]
    assert signals.mean(axis=1).iloc[0] == pytest.approx(0.0)
    assert signals.std(axis=1).iloc[0] == pytest.approx(1.0)


def test_commodity_carry_sign():
    idx = pd.date_range("2020-01-01", periods=1)
    near = pd.DataFrame({"A": [100], "B": [100]}, index=idx)
    far = pd.DataFrame({"A": [98], "B": [105]}, index=idx)
    signals = commodity_carry(near, far, days_to_expiry=30)
    row = signals.iloc[0]
    assert row["A"] > row["B"]
    assert signals.mean(axis=1).iloc[0] == pytest.approx(0.0)
    assert signals.std(axis=1).iloc[0] == pytest.approx(1.0)


def test_fx_carry():
    idx = pd.date_range("2020-01-01", periods=1)
    domestic = pd.DataFrame({"EURUSD": [0.02], "USDJPY": [0.01]}, index=idx)
    foreign = pd.DataFrame({"EURUSD": [0.005], "USDJPY": [0.03]}, index=idx)
    signals = fx_carry(domestic, foreign)
    row = signals.iloc[0]
    assert row["EURUSD"] > row["USDJPY"]
    assert signals.mean(axis=1).iloc[0] == pytest.approx(0.0)
    assert signals.std(axis=1).iloc[0] == pytest.approx(1.0)
