import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from optimizer import combine_sleeves


def test_combine_sleeves_equal():
    trend = pd.Series({"A": 0.6, "B": 0.4})
    carry = pd.Series({"A": 0.2, "B": 0.8})
    combined = combine_sleeves(trend, carry)
    expected = 0.5 * trend + 0.5 * carry
    assert combined.equals(expected)


def test_combine_sleeves_risk_parity_downweights_vol():
    trend = pd.Series({"A": 0.6, "B": 0.4})
    carry = pd.Series({"A": 0.2, "B": 0.8})
    # trend sleeve is more volatile
    rng = np.random.default_rng(0)
    ret_trend = rng.normal(0, 0.02, 100)
    ret_carry = rng.normal(0, 0.01, 100)
    returns = pd.DataFrame({"trend": ret_trend, "carry": ret_carry})
    combined = combine_sleeves(trend, carry, returns=returns, method="risk_parity")
    # Risk parity should allocate less than 50% to the more volatile trend sleeve
    combined_equal = 0.5 * trend + 0.5 * carry
    assert combined["A"] < combined_equal["A"]
    assert combined["B"] > combined_equal["B"]
