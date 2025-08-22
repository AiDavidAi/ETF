import numpy as np
import pandas as pd


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional z-score for each row.

    Parameters
    ----------
    df : pd.DataFrame
        Values to standardize.

    Returns
    -------
    pd.DataFrame
        Z-scored values with NaNs/infs replaced by zero.
    """
    if df.empty:
        return pd.DataFrame(index=df.index, columns=df.columns)
    mean = df.mean(axis=1)
    std = df.std(axis=1).replace(0, np.nan)
    z = df.sub(mean, axis=0).div(std, axis=0)
    return z.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def equity_carry(
    dividend_yield: pd.DataFrame,
    financing_rate: pd.DataFrame | pd.Series | float,
) -> pd.DataFrame:
    """Standardized equity carry.

    Carry approximated as ``dividend_yield - financing_rate``.
    ``financing_rate`` can be a scalar, Series, or DataFrame.
    """
    if isinstance(financing_rate, (int, float)):
        fr = pd.DataFrame(
            financing_rate, index=dividend_yield.index, columns=dividend_yield.columns
        )
    elif isinstance(financing_rate, pd.Series):
        fr = pd.DataFrame(
            np.repeat(financing_rate.values[:, None], dividend_yield.shape[1], axis=1),
            index=dividend_yield.index,
            columns=dividend_yield.columns,
        )
    else:
        fr = financing_rate.reindex_like(dividend_yield)
    carry = dividend_yield - fr
    return _standardize(carry)


def bond_carry(yields: pd.DataFrame, roll_down: pd.DataFrame) -> pd.DataFrame:
    """Standardized bond carry computed as yield plus roll-down."""
    carry = yields.add(roll_down, fill_value=0.0)
    return _standardize(carry)


def commodity_carry(
    near: pd.DataFrame,
    far: pd.DataFrame,
    days_to_expiry: int,
    days_in_year: int = 365,
) -> pd.DataFrame:
    """Standardized commodity carry based on term-structure slope.

    Parameters
    ----------
    near : pd.DataFrame
        Prices of the near contract.
    far : pd.DataFrame
        Prices of a further-out contract with the same expiry distance.
    days_to_expiry : int
        Days until the near contract expires.
    days_in_year : int, optional
        Annualization factor. Default is 365.
    """
    if near.empty:
        return pd.DataFrame(index=near.index, columns=near.columns)
    far_aligned = far.reindex_like(near)
    slope = (far_aligned / near - 1.0) * (days_in_year / days_to_expiry)
    carry = -slope
    return _standardize(carry)
