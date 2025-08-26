import os
import sys

import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from signals import predict_regime_probability, train_logistic_regime_model


def test_regime_training_and_prediction() -> None:
    features = pd.DataFrame({"x": [0, 1, 2, 3]}, index=pd.RangeIndex(4))
    labels = pd.Series([0, 0, 1, 1], index=features.index)
    model = train_logistic_regime_model(features, labels)
    probs = predict_regime_probability(features, model)
    assert probs.iloc[0] < 0.5
    assert probs.iloc[-1] > 0.5
    assert model.scaler.mean_[0] == pytest.approx(1.5)
