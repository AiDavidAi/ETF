"""Index constituent and price retrieval utilities."""

from __future__ import annotations

from typing import List, Literal, Mapping, Tuple

import pandas as pd
import yfinance as yf

IndexName = Literal["sp500", "dow", "nasdaq", "russell2000"]

_INDEX_SOURCES: Mapping[IndexName, Tuple[str, str]] = {
    "sp500": ("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", "Symbol"),
    "dow": ("https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average", "Symbol"),
    "nasdaq": (
        "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed.csv",
        "Symbol",
    ),
    "russell2000": ("https://en.wikipedia.org/wiki/Russell_2000_Index", "Ticker"),
}


def _load_table(url: str) -> pd.DataFrame:
    """Load a table of data from an HTML or CSV source.

    Parameters
    ----------
    url:
        Location of the CSV or HTML file to load.

    Returns
    -------
    pd.DataFrame
        Parsed table.
    """
    if url.endswith(".csv"):
        return pd.read_csv(url)
    tables: List[pd.DataFrame] = pd.read_html(url)
    if not tables:
        msg = f"no tables found at {url}"
        raise ValueError(msg)
    return tables[0]


def get_index_tickers(index: IndexName) -> List[str]:
    """Return the list of ticker symbols for a market index.

    Parameters
    ----------
    index:
        Name of the index to query. Supported values are ``"sp500"``, ``"dow"``,
        ``"nasdaq"`` and ``"russell2000"``.

    Returns
    -------
    list of str
        Sorted list of ticker symbols.
    """
    url, column = _INDEX_SOURCES[index]
    table = _load_table(url)
    if column not in table.columns:
        msg = f"column '{column}' not found in table from {url}"
        raise KeyError(msg)
    tickers = table[column].astype(str).str.upper().unique()
    return sorted(tickers.tolist())


def fetch_current_prices(index: IndexName) -> pd.Series:
    """Fetch the latest available prices for all securities in an index.

    Parameters
    ----------
    index:
        Name of the index to download data for.

    Returns
    -------
    pd.Series
        Series indexed by ticker symbol containing the most recent price.
    """
    tickers = get_index_tickers(index)
    close = yf.download(tickers, period="1d", interval="1m", progress=False)["Close"]
    if isinstance(close, pd.Series):
        data = pd.Series({tickers[0]: float(close.iloc[-1])})
    else:
        data = close.iloc[-1].astype(float)
    data.name = "price"
    return data


def fetch_historical_data(
    index: IndexName, start: pd.Timestamp, end: pd.Timestamp
) -> pd.DataFrame:
    """Fetch historical OHLCV data for all securities in an index.

    Parameters
    ----------
    index:
        Name of the index to download data for.
    start:
        Start date of the historical period.
    end:
        End date of the historical period.

    Returns
    -------
    pd.DataFrame
        DataFrame with a column MultiIndex of field and ticker symbol.
    """
    tickers = get_index_tickers(index)
    data = yf.download(tickers, start=start, end=end, group_by="ticker", progress=False)
    return data
