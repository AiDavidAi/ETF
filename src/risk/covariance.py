import numpy as np
import pandas as pd

try:
    from sklearn.covariance import LedoitWolf as _LedoitWolf
except Exception:  # pragma: no cover - optional dependency
    _LedoitWolf = None

try:
    from scipy.cluster.hierarchy import linkage
    from scipy.spatial.distance import squareform
except Exception:  # pragma: no cover - required for HRP
    linkage = None
    squareform = None


def sample_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """Plain sample covariance of returns."""
    return returns.cov()


def ledoit_wolf(returns: pd.DataFrame) -> pd.DataFrame:
    """Ledoit–Wolf shrinkage estimator of the covariance matrix.

    Parameters
    ----------
    returns : pd.DataFrame
        Matrix of asset returns with assets in columns.

    Returns
    -------
    pd.DataFrame
        Shrunk covariance matrix. Falls back to sample covariance if
        scikit-learn is unavailable.
    """
    if _LedoitWolf is None:
        return sample_covariance(returns)

    model = _LedoitWolf().fit(returns.values)
    cov = pd.DataFrame(model.covariance_, index=returns.columns, columns=returns.columns)
    return cov


def _get_ivp(cov: pd.DataFrame) -> pd.Series:
    """Compute the inverse-variance portfolio for a covariance matrix."""
    iv = 1.0 / np.diag(cov)
    ivp = iv / iv.sum()
    return pd.Series(ivp, index=cov.index)


def _get_cluster_var(cov: pd.DataFrame) -> float:
    w = _get_ivp(cov)
    return float(w.values @ cov.values @ w.values)


def _quasi_diag(link) -> list[int]:
    link = link.astype(int)
    sort_ix = [link[-1, 0], link[-1, 1]]
    n_items = link[-1, 3]
    while max(sort_ix) >= n_items:
        sort_ix = [
            j if j < n_items else link[j - n_items, 0]
            for i in sort_ix
            for j in ([link[i - n_items, 0], link[i - n_items, 1]] if i >= n_items else [i])
        ]
    return sort_ix


def _recursive_bisection(cov: pd.DataFrame, sorted_ix: list[int]) -> pd.Series:
    w = pd.Series(1.0, index=cov.index[sorted_ix])
    clusters = [list(w.index)]
    while clusters:
        cluster = clusters.pop(0)
        if len(cluster) <= 1:
            continue
        split = len(cluster) // 2
        left = cluster[:split]
        right = cluster[split:]
        cov_left = cov.loc[left, left]
        cov_right = cov.loc[right, right]
        var_left = _get_cluster_var(cov_left)
        var_right = _get_cluster_var(cov_right)
        alpha = 0.0
        if (var_left + var_right) > 0:
            alpha = 1 - var_left / (var_left + var_right)
        w[left] *= alpha
        w[right] *= 1 - alpha
        clusters += [left, right]
    return w


def hrp_weights(returns: pd.DataFrame) -> pd.Series:
    """Hierarchical Risk Parity portfolio weights.

    Parameters
    ----------
    returns : pd.DataFrame
        Asset return history with assets in columns.

    Returns
    -------
    pd.Series
        HRP weights that sum to one.
    """
    if linkage is None or squareform is None:
        raise ImportError("scipy is required for HRP weights")

    corr = returns.corr().fillna(0.0)
    dist = np.sqrt(0.5 * (1 - corr))
    condensed = squareform(dist.values, checks=False)
    link = linkage(condensed, method="single")
    sort_ix = _quasi_diag(link)
    sorted_labels = corr.index[sort_ix]
    cov = returns.cov().loc[sorted_labels, sorted_labels]
    w = _recursive_bisection(cov, list(range(len(cov))))
    w = w.reindex(returns.columns).fillna(0)
    w = w / w.sum()
    return w
