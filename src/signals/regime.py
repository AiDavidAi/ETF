"""Regime classification using logistic regression."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


@dataclass
class LogisticRegimeModel:
    """Container for a fitted logistic regression regime model."""

    model: LogisticRegression
    scaler: StandardScaler
    columns: List[str]


def train_logistic_regime_model(
    features: pd.DataFrame,
    labels: pd.Series,
    *,
    C: float = 1.0,
    penalty: str = "l2",
    solver: str = "lbfgs",
) -> LogisticRegimeModel:
    """Train a logistic regression model for regime classification.

    Parameters
    ----------
    features
        Feature matrix indexed by date.
    labels
        Binary labels where 1 indicates risk-off.
    C
        Inverse of regularization strength passed to ``LogisticRegression``.
    penalty
        Regularization penalty to apply.
    solver
        Optimization algorithm used by ``LogisticRegression``.

    Returns
    -------
    LogisticRegimeModel
        Fitted logistic regression model and feature scaler.
    """

    scaler = StandardScaler()
    model = LogisticRegression(C=C, penalty=penalty, solver=solver)

    if features.empty:
        return LogisticRegimeModel(
            model=model, scaler=scaler, columns=list(features.columns)
        )

    X = scaler.fit_transform(features.values)
    model.fit(X, labels.values)
    return LogisticRegimeModel(
        model=model, scaler=scaler, columns=list(features.columns)
    )


def predict_regime_probability(
    features: pd.DataFrame, regime_model: LogisticRegimeModel
) -> pd.Series:
    """Predict risk-off probabilities using a trained regime model."""

    if features.empty:
        return pd.Series(index=features.index, dtype=float)

    aligned = features.reindex(columns=regime_model.columns).fillna(0.0).values
    X = regime_model.scaler.transform(aligned)
    probs = regime_model.model.predict_proba(X)[:, 1]
    return pd.Series(probs, index=features.index)
