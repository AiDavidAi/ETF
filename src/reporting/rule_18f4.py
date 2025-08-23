import pandas as pd


def generate_18f4_report(var: pd.Series, exposure: pd.Series, limit: float) -> pd.DataFrame:
    """Create a simple 18f-4 compliance report.

    Parameters
    ----------
    var : pd.Series
        Portfolio VaR figures indexed by date.
    exposure : pd.Series
        Derivatives exposure as a fraction of NAV.
    limit : float
        VaR limit threshold.

    Returns
    -------
    pd.DataFrame
        Report with VaR, exposure, limit, and breach flag.
    """
    df = pd.DataFrame({"VaR": var, "Exposure": exposure})
    df["limit"] = limit
    breach = (df["VaR"] > limit) | (df["Exposure"] > 1.0)
    df["breach"] = pd.Series([bool(x) for x in breach], index=df.index, dtype=object)
    return df
