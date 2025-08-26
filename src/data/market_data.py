"""Utilities for retrieving market data from external sources."""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_ohlcv(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Fetch historical OHLCV data for a given ticker.

    Parameters
    ----------
    ticker:
        Symbol of the security to download.
    start:
        Start date of the data range.
    end:
        End date of the data range.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date with columns ``open``, ``high``, ``low``,
        ``close``, ``adj_close`` and ``volume``.
    """
    data = yf.download(ticker, start=start, end=end, progress=False)
    data = data.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    return data[["open", "high", "low", "close", "adj_close", "volume"]]
