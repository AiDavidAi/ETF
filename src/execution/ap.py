import pandas as pd


def process_ap_flows(creations: int, redemptions: int, basket: pd.Series) -> pd.Series:
    """Calculate net asset flows from AP creations and redemptions.

    Parameters
    ----------
    creations : int
        Number of creation units.
    redemptions : int
        Number of redemption units.
    basket : pd.Series
        Quantity of each asset per creation unit.

    Returns
    -------
    pd.Series
        Net asset flows to execute. Positive values indicate buys.
    """
    net = creations - redemptions
    return basket * net
