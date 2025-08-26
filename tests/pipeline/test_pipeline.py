import pandas as pd

from src.pipeline import run_daily_cycle


def test_run_daily_cycle_smoke() -> None:
    dates = pd.date_range("2021-01-01", periods=5)
    contract_data = pd.DataFrame(
        {
            "asset": ["A"] * 5 + ["B"] * 5,
            "date": list(dates) * 2,
            "contract": ["A1"] * 5 + ["B1"] * 5,
            "price": [100, 101, 102, 103, 104] + [50, 51, 52, 53, 54],
            "volume": [1000] * 10,
            "open_interest": [1000] * 10,
            "expiry": [dates[-1] + pd.Timedelta(days=30)] * 10,
        }
    )
    dividend_yield = pd.DataFrame(0.02, index=dates, columns=["A", "B"])
    returns = pd.DataFrame(
        {
            "A": [0.0, 0.01, -0.02, 0.015, 0.0],
            "B": [0.0, -0.005, 0.01, -0.01, 0.005],
        },
        index=dates,
    )
    features = returns.copy()
    labels = pd.Series([0, 1, 0, 1, 0], index=dates)
    current_weights = pd.Series({"A": 0.0, "B": 0.0})
    multipliers = pd.Series({"A": 1.0, "B": 1.0})
    fx_rates = pd.Series({"A": 1.0, "B": 1.0})
    capital = 1_000_000.0
    margin_rates = pd.Series({"A": 0.1, "B": 0.1})
    cost_estimates = pd.Series(
        [1.0, 2.0, 3.0], index=pd.date_range("2021-01-06", periods=3, freq="H")
    )
    result = run_daily_cycle(
        contract_data=contract_data,
        dividend_yield=dividend_yield,
        financing_rate=0.01,
        features=features,
        regime_labels=labels,
        current_weights=current_weights,
        multipliers=multipliers,
        fx_rates=fx_rates,
        capital=capital,
        margin_rates=margin_rates,
        returns=returns,
        cost_estimates=cost_estimates,
        var_limit=0.2,
    )
    assert "orders" in result and not result["orders"].empty
    assert "report" in result and not result["report"].empty
