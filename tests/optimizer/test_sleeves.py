import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from optimizer import combine_sleeves, erc


def test_combine_sleeves_equal():
    trend = pd.Series({"A": 0.6, "B": 0.4})
    carry = pd.Series({"A": 0.2, "B": 0.8})
    combined = combine_sleeves(trend, carry)
    expected = 0.5 * trend + 0.5 * carry
    assert combined.equals(expected)


def test_combine_sleeves_risk_parity_uses_erc():
    trend = pd.Series({"A": 0.6, "B": 0.4})
    carry = pd.Series({"A": 0.2, "B": 0.8})
    rng = np.random.default_rng(0)
    ret_trend = rng.normal(0, 0.02, 100)
    ret_carry = rng.normal(0, 0.01, 100)
    returns = pd.DataFrame({"trend": ret_trend, "carry": ret_carry})
    combined = combine_sleeves(trend, carry, returns=returns, method="risk_parity")
    # Explicitly compute ERC mix for comparison
    mix = erc(returns[["trend", "carry"]].cov())
    expected = mix["trend"] * trend + mix["carry"] * carry
    pd.testing.assert_series_equal(combined, expected)
