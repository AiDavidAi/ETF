from __future__ import annotations

import argparse
from typing import Iterable, cast

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]


def recommend_etfs(
    tickers: Iterable[str], lookback: int = 252, top_n: int = 5
) -> pd.Series:
    """Rank ETFs by total return over a lookback window.

    Parameters
    ----------
    tickers:
        Iterable of ETF ticker symbols.
    lookback:
        Number of calendar days of history to consider.
    top_n:
        Number of top-performing ETFs to return.

    Returns
    -------
    pd.Series
        Series indexed by ticker symbol containing total returns sorted
        from best to worst.
    """
    tickers_list = [t.upper() for t in tickers]
    data = yf.download(tickers_list, period=f"{lookback}d", progress=False)["Close"]
    if isinstance(data, pd.Series):
        returns = data.iloc[-1] / data.iloc[0] - 1.0
        returns = pd.Series({tickers_list[0]: float(returns)})
    else:
        returns = data.iloc[-1] / data.iloc[0] - 1.0
        returns = returns.astype(float)
    sorted_returns = returns.sort_values(ascending=False).head(top_n)
    return cast(pd.Series, sorted_returns)


def main() -> None:
    """CLI entry point for generating ETF recommendations."""
    parser = argparse.ArgumentParser(
        description="Rank ETFs by recent performance using yfinance data"
    )
    parser.add_argument("tickers", nargs="+", help="ETF tickers to evaluate")
    parser.add_argument(
        "--lookback", type=int, default=252, help="Historical window in days"
    )
    parser.add_argument(
        "--top", type=int, default=5, help="Number of tickers to return"
    )
    args = parser.parse_args()
    recs = recommend_etfs(args.tickers, lookback=args.lookback, top_n=args.top)
    print(recs.to_string())


if __name__ == "__main__":
    main()
