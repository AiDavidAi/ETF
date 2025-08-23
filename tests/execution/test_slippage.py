import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import estimate_slippage


def test_estimate_slippage():
    spread = pd.Series({"ES": 0.5, "NQ": 1.0})
    vol = pd.Series({"ES": 1.0, "NQ": 2.0})
    part = pd.Series({"ES": 0.04, "NQ": 0.01})
    result = estimate_slippage(spread, vol, part, alpha=0.1)
    expected = spread / 2 + 0.1 * vol * part.pow(0.5)
    pd.testing.assert_series_equal(result, expected)
