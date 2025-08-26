import pandas as pd
import pytest

from src.optimizer.erc import erc


def test_erc_accepts_covariance_matrix():
    cov = pd.DataFrame(
        [[0.1, 0.02, 0.03], [0.02, 0.2, 0.04], [0.03, 0.04, 0.15]],
        columns=["A", "B", "C"],
        index=["A", "B", "C"],
    )
    weights = erc(cov)
    assert isinstance(weights, pd.Series)
    assert list(weights.index) == ["A", "B", "C"]
    assert weights.sum() == pytest.approx(1.0)


def test_erc_weights_normalized():
    cov = pd.DataFrame(
        [[0.05, 0.01], [0.01, 0.03]],
        columns=["X", "Y"],
        index=["X", "Y"],
    )
    weights = erc(cov)
    assert weights.sum() == pytest.approx(1.0)
    assert all(weights >= 0)
