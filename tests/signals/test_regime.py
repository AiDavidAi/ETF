import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from signals import train_logistic_regime_model, predict_regime_probability


def test_regime_training_and_prediction():
    features = pd.DataFrame({"x": [0, 1, 2, 3]}, index=pd.RangeIndex(4))
    labels = pd.Series([0, 0, 1, 1], index=features.index)
    weights = train_logistic_regime_model(features, labels, lr=0.5, epochs=2000)
    probs = predict_regime_probability(features, weights)
    assert probs.iloc[0] < 0.5
    assert probs.iloc[-1] > 0.5
