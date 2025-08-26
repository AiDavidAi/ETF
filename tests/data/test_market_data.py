import pandas as pd
import pytest
import yfinance as yf

from src.data import fetch_ohlcv


def test_fetch_ohlcv_returns_data(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(
        ticker: str, start: pd.Timestamp, end: pd.Timestamp, progress: bool = False
    ) -> pd.DataFrame:
        index = pd.date_range(start, periods=2)
        return pd.DataFrame(
            {
                "Open": [1.0, 2.0],
                "High": [1.0, 2.0],
                "Low": [1.0, 2.0],
                "Close": [1.0, 2.0],
                "Adj Close": [1.0, 2.0],
                "Volume": [100, 200],
            },
            index=index,
        )

    monkeypatch.setattr(yf, "download", fake_download)
    end = pd.Timestamp("2024-01-03")
    start = end - pd.Timedelta(days=1)
    df = fetch_ohlcv("SPY", start=start, end=end)
    assert not df.empty
    assert {"open", "high", "low", "close", "adj_close", "volume"}.issubset(df.columns)
