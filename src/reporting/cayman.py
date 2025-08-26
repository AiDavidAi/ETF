from typing import Iterable, Tuple

import pandas as pd


def allocate_cayman(
    weights: pd.DataFrame, commodity_symbols: Iterable[str], limit: float = 0.25
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split portfolio weights between domestic fund and Cayman subsidiary.

    The Cayman subsidiary holds commodity positions subject to a weight limit.

    Parameters
    ----------
    weights : pd.DataFrame
        Portfolio weights indexed by date.
    commodity_symbols : Iterable[str]
        Columns representing commodity exposures.
    limit : float, optional
        Maximum absolute total commodity weight.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        ``(domestic, cayman)`` DataFrames with same shape as ``weights``.
    """
    commodity_symbols = list(commodity_symbols)
    missing = set(commodity_symbols) - set(weights.columns)
    if missing:
        raise ValueError(f"Unknown commodity symbols: {sorted(missing)}")

    domestic = weights.copy()
    cayman = weights.copy()
    domestic[commodity_symbols] = 0.0
    cayman[[c for c in weights.columns if c not in commodity_symbols]] = 0.0

    if (cayman.abs().sum(axis=1) > limit).any():
        raise ValueError("Commodity exposure exceeds limit")

    return domestic, cayman
