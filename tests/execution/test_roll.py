import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import roll_weights


def test_roll_weights():
    dte = pd.Series({"A": 40, "B": 5, "C": 0})
    frac = roll_weights(dte, window=10)
    assert frac["A"] == pytest.approx(0.0)
    assert frac["B"] == pytest.approx(0.5)
    assert frac["C"] == pytest.approx(1.0)
