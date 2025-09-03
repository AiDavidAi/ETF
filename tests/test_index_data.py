import pandas as pd
import pytest
import yfinance as yf

from src.data import index_data


def test_get_index_tickers_html(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_read_html(url: str) -> list[pd.DataFrame]:
        return [pd.DataFrame({"Symbol": ["AAA", "BBB"]})]

    monkeypatch.setattr(pd, "read_html", fake_read_html)
    tickers = index_data.get_index_tickers("sp500")
    assert tickers == ["AAA", "BBB"]


def test_get_index_tickers_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_read_csv(url: str) -> pd.DataFrame:
        return pd.DataFrame({"Symbol": ["CCC", "DDD"]})

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    tickers = index_data.get_index_tickers("nasdaq")
    assert tickers == ["CCC", "DDD"]


def test_fetch_current_prices(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_index_tickers(index: index_data.IndexName) -> list[str]:
        return ["AAA", "BBB"]

    def fake_download(*args: object, **kwargs: object) -> pd.DataFrame:
        idx = pd.date_range("2024-01-01", periods=2, freq="1min")
        cols = pd.MultiIndex.from_product([["Close"], ["AAA", "BBB"]])
        data = pd.DataFrame([[10.0, 20.0], [11.0, 21.0]], index=idx, columns=cols)
        return data

    monkeypatch.setattr(index_data, "get_index_tickers", fake_get_index_tickers)
    monkeypatch.setattr(yf, "download", fake_download)
    monkeypatch.setattr(index_data, "yf", yf)
    prices = index_data.fetch_current_prices("sp500")
    assert prices.to_dict() == {"AAA": 11.0, "BBB": 21.0}


def test_fetch_historical_data(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_index_tickers(index: index_data.IndexName) -> list[str]:
        return ["AAA"]

    def fake_download(*args: object, **kwargs: object) -> pd.DataFrame:
        return pd.DataFrame({("Close", "AAA"): [1.0]})

    monkeypatch.setattr(index_data, "get_index_tickers", fake_get_index_tickers)
    monkeypatch.setattr(yf, "download", fake_download)
    monkeypatch.setattr(index_data, "yf", yf)
    df = index_data.fetch_historical_data(
        "sp500", pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")
    )
    assert not df.empty
