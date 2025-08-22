import pandas as pd
from typing import Union
from pathlib import Path


def generate_dashboard(
    portfolio: pd.DataFrame,
    var_value: float,
    path: Union[str, Path],
) -> None:
    """Write a minimal dashboard CSV containing portfolio value and VaR.

    Parameters
    ----------
    portfolio : pd.DataFrame
        DataFrame indexed by date containing at least a ``value`` column.
    var_value : float
        VaR figure to display alongside the portfolio series.
    path : Union[str, Path]
        Output file path.
    """

    out = portfolio.copy()
    out["VaR99_20d"] = var_value
    path = Path(path)
    out.to_csv(path)
