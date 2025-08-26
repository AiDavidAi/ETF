import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from risk import scale_to_target_vol


def test_scale_to_target_vol_returns_expected_factor():
    returns = pd.Series([0.01, -0.01] * 126)
    target = 0.2
    expected = target / (returns.std(ddof=0) * np.sqrt(252))
    factor = scale_to_target_vol(returns, target, window=252)
    assert np.isclose(factor, expected)


def test_scale_to_target_vol_zero_volatility():
    returns = pd.Series([0.0] * 252)
    factor = scale_to_target_vol(returns, 0.2)
    assert factor == 0.0
