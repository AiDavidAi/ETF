import numpy as np
import pandas as pd


def train_logistic_regime_model(
    features: pd.DataFrame, labels: pd.Series, lr: float = 0.1, epochs: int = 1000
) -> pd.Series:
    """Train a simple logistic regression model for regime classification.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix indexed by date.
    labels : pd.Series
        Binary labels where 1 indicates risk-off.
    lr : float, optional
        Learning rate for gradient descent.
    epochs : int, optional
        Number of optimization iterations.

    Returns
    -------
    pd.Series
        Learned weights including a bias term.
    """

    if features.empty:
        return pd.Series(dtype=float)

    X = features.values
    y = labels.values.astype(float)
    X_b = np.c_[np.ones(len(X)), X]
    w = np.zeros(X_b.shape[1])

    for _ in range(epochs):
        z = X_b @ w
        p = 1.0 / (1.0 + np.exp(-z))
        gradient = X_b.T @ (p - y) / len(y)
        w -= lr * gradient

    index = ["bias"] + list(features.columns)
    return pd.Series(w, index=index)


def predict_regime_probability(features: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Predict risk-off probabilities using logistic regression weights."""
    if features.empty:
        return pd.Series(index=features.index, dtype=float)

    X_b = np.c_[np.ones(len(features)), features.values]
    w = weights.reindex(["bias"] + list(features.columns)).fillna(0.0).values
    probs = 1.0 / (1.0 + np.exp(-(X_b @ w)))
    return pd.Series(probs, index=features.index)
