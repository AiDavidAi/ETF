import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from risk.var import calculate_var


def test_calculate_var():
    returns = pd.Series(np.linspace(-0.05, 0.05, 100))
    expected = -np.quantile(returns, 0.01) * np.sqrt(20)
    var = calculate_var(returns)
    assert var == pytest.approx(expected)
