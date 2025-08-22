import numpy as np
import pandas as pd
from typing import Union, Optional

try:
    from scipy.optimize import minimize
except ImportError as e:  # pragma: no cover
    raise ImportError("scipy is required for the ERC optimizer") from e


def erc(
    cov: Union[pd.DataFrame, np.ndarray],
    target_vol: Optional[float] = None,
) -> pd.Series:
    """Compute Equal Risk Contribution (ERC) portfolio weights.

    The ERC portfolio allocates capital such that each asset contributes
    equally to the overall portfolio risk. Optionally, the resulting weights
    can be leveraged to target a specific portfolio volatility.

    Parameters
    ----------
    cov : Union[pd.DataFrame, np.ndarray]
        Covariance matrix of asset returns. Can be provided as a pandas
        DataFrame or a NumPy array. When a DataFrame is provided, the returned
        Series will use its column names as the index.
    target_vol : float, optional
        If provided, scale the weights so that the portfolio volatility matches
        ``target_vol``.

    Returns
    -------
    pd.Series
        Portfolio weights. If ``target_vol`` is supplied the weights include the
        leverage required to hit the target volatility.
    """

    if isinstance(cov, pd.DataFrame):
        cov_matrix = cov.values
        labels = cov.columns
    else:
        cov_matrix = np.asarray(cov)
        labels = pd.Index(range(cov_matrix.shape[0]))

    if cov_matrix.shape[0] != cov_matrix.shape[1]:
        raise ValueError("Covariance matrix must be square")

    n_assets = cov_matrix.shape[0]

    def risk_contribution(weights: np.ndarray) -> tuple[np.ndarray, float]:
        portfolio_var = float(weights @ cov_matrix @ weights)
        marginal_contrib = cov_matrix @ weights
        rc = weights * marginal_contrib
        return rc, portfolio_var

    def objective(weights: np.ndarray) -> float:
        rc, portfolio_var = risk_contribution(weights)
        target_rc = portfolio_var / n_assets
        return float(((rc - target_rc) ** 2).sum())

    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, None)] * n_assets
    x0 = np.full(n_assets, 1.0 / n_assets)

    res = minimize(objective, x0, bounds=bounds, constraints=constraints)
    if not res.success:  # pragma: no cover
        raise ValueError("Optimization failed: " + res.message)

    weights = res.x

    if target_vol is not None:
        _, portfolio_var = risk_contribution(weights)
        current_vol = np.sqrt(portfolio_var)
        if current_vol > 0:
            leverage = target_vol / current_vol
            weights = weights * leverage

    return pd.Series(weights, index=labels)
