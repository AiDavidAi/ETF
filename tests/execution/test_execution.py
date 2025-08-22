import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import weights_to_contracts, generate_twap_schedule


def test_weights_to_contracts():
    date = pd.Timestamp("2020-01-01")
    weights = pd.DataFrame({"ES": [0.4], "DAX": [0.3]}, index=[date])
    prices = pd.DataFrame({"ES": [4000], "DAX": [15000]}, index=[date])
    multipliers = pd.Series({"ES": 50, "DAX": 25})
    fx = pd.Series({"ES": 1.0, "DAX": 1.1})
    capital = 1_000_000
    contracts = weights_to_contracts(weights, prices, multipliers, fx, capital)
    assert contracts.loc[date, "ES"] == 2
    assert contracts.loc[date, "DAX"] == 1


def test_generate_twap_schedule():
    start = pd.Timestamp("2021-01-01 09:30")
    end = pd.Timestamp("2021-01-01 10:30")
    sched = generate_twap_schedule(100, start, end, slices=4)
    assert len(sched) == 4
    assert sched["quantity"].sum() == 100
    assert sched["time"].iloc[0] == start
    assert sched["time"].iloc[-1] == end
    diff = sched["time"].diff().dropna()
    expected = (end - start) / (len(sched) - 1)
    assert all(diff == expected)
