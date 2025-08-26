import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from risk import scale_by_drawdown


def test_scale_by_drawdown_partial():
    equity = pd.Series([100, 100, 90])
    scale = scale_by_drawdown(equity, max_drawdown=0.2)
    assert np.isclose(scale, 0.5)


def test_scale_by_drawdown_full_reduction():
    equity = pd.Series([100, 100, 70])
    scale = scale_by_drawdown(equity, max_drawdown=0.2)
    assert scale == 0.0
