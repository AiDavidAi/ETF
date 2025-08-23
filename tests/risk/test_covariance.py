import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from risk import ledoit_wolf, hrp_weights


def _sample_returns():
    rng = np.random.default_rng(0)
    data = rng.normal(size=(200, 3))
    return pd.DataFrame(data, columns=list("ABC"))


def test_ledoit_wolf_positive_semidefinite():
    returns = _sample_returns()
    cov = ledoit_wolf(returns)
    vals = np.linalg.eigvalsh(cov.values)
    assert cov.shape == (3, 3)
    assert (vals >= -1e-8).all()


def test_hrp_weights_sum_to_one_and_non_negative():
    returns = _sample_returns()
    weights = hrp_weights(returns)
    assert np.isclose(weights.sum(), 1.0)
    assert (weights >= 0).all()
