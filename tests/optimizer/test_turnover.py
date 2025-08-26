import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from optimizer import penalized_band_weights


def test_penalized_band_weights():
    target = pd.Series({"A": 0.5, "B": 0.0})
    current = pd.Series({"A": 0.0, "B": 0.5})
    adjusted = penalized_band_weights(target, current, band=0.1, penalty=0.5)
    assert adjusted["A"] == pytest.approx(0.25)
    assert adjusted["B"] == pytest.approx(0.25)
    # ensure banding unchanged within threshold
    target2 = pd.Series({"A": 0.55, "B": 0.45})
    adjusted2 = penalized_band_weights(target2, current, band=0.1, penalty=0.5)
    # difference for A =0.55-0.0=0.55->adjust ->0.275 but B diff= -0.05 within band -> stays 0.5
    assert adjusted2["B"] == pytest.approx(0.5)
