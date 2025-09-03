import pandas as pd
import pytest

from src import recommendations


def test_recommend_etfs(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(*args: object, **kwargs: object) -> pd.DataFrame:
        idx = pd.date_range("2024-01-01", periods=2, freq="1D")
        cols = pd.MultiIndex.from_product([["Close"], ["AAA", "BBB", "CCC"]])
        data = pd.DataFrame(
            [[10.0, 10.0, 10.0], [11.0, 9.0, 12.0]], index=idx, columns=cols
        )
        return data

    monkeypatch.setattr(recommendations.yf, "download", fake_download)
    result = recommendations.recommend_etfs(["AAA", "BBB", "CCC"], lookback=2, top_n=2)
    assert result.index.tolist() == ["CCC", "AAA"]
