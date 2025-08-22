import pandas as pd
from src.optimizer.turnover import band_weights


def test_band_weights_within_band():
    current = pd.Series({"A": 0.5, "B": 0.5})
    target = pd.Series({"A": 0.52, "B": 0.48})
    adjusted = band_weights(target, current, band=0.05)
    pd.testing.assert_series_equal(adjusted, current, check_names=False)


def test_band_weights_outside_band():
    current = pd.Series({"A": 0.5, "B": 0.5})
    target = pd.Series({"A": 0.7, "B": 0.3})
    adjusted = band_weights(target, current, band=0.05)
    pd.testing.assert_series_equal(adjusted, target, check_names=False)
