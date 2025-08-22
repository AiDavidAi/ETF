import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from signals import volatility_scaled_momentum


def test_volatility_scaled_momentum_sign():
    prices = pd.DataFrame(
        {
            "A": [100, 101, 102, 103],
            "B": [100, 99, 98, 97],
        },
        index=pd.date_range("2020-01-01", periods=4),
    )
    signals = volatility_scaled_momentum(prices, lookback=3, vol_lookback=3)
    last = signals.iloc[-1]
    assert last["A"] > 0
    assert last["B"] < 0


def test_volatility_scaling():
    prices = pd.DataFrame(
        {"A": [100, 102, 101, 103, 105]},
        index=pd.date_range("2020-01-01", periods=5),
    )
    lookback = 2
    vol_lookback = 3
    signals = volatility_scaled_momentum(
        prices, lookback=lookback, vol_lookback=vol_lookback
    )
    last_signal = signals.iloc[-1, 0]
    momentum = prices.pct_change(lookback).iloc[-1, 0]
    returns = prices.pct_change()
    vol = returns.rolling(vol_lookback).std().iloc[-1, 0]
    expected = momentum / vol
    assert last_signal == pytest.approx(expected)
