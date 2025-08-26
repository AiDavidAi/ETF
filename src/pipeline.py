"""Pipeline orchestrating the daily trading workflow."""

from __future__ import annotations

import argparse
from typing import Any, Dict

import pandas as pd

from .data.continuous_futures import construct_continuous_futures
from .execution import plan_orders, weights_to_contracts
from .optimizer.erc import erc
from .optimizer.turnover import penalized_band_weights
from .reporting.rule_18f4 import generate_18f4_report
from .risk.margin import forecast_margin
from .risk.var import calculate_var
from .signals.carry import equity_carry
from .signals.regime import predict_regime_probability, train_logistic_regime_model
from .signals.trend import volatility_scaled_momentum


def run_daily_cycle(
    contract_data: pd.DataFrame,
    dividend_yield: pd.DataFrame,
    financing_rate: float,
    features: pd.DataFrame,
    regime_labels: pd.Series,
    current_weights: pd.Series,
    multipliers: pd.Series,
    fx_rates: pd.Series,
    capital: float,
    margin_rates: pd.Series,
    returns: pd.DataFrame,
    cost_estimates: pd.Series,
    var_limit: float,
    band: float = 0.01,
    penalty: float = 0.5,
    target_vol: float = 0.1,
) -> Dict[str, Any]:
    """Run a complete daily cycle for the trading system.

    The function performs the following high-level steps:

    1. Load and update data from raw contract information.
    2. Compute trend, carry, and regime signals.
    3. Optimize target positions using ERC and turnover controls.
    4. Run risk checks including VaR, margin, and drawdown.
    5. Translate weights into contract orders and schedule execution.
    6. Generate a simple compliance report.

    Parameters
    ----------
    contract_data:
        Raw futures contract data containing ``asset`` and price information.
    dividend_yield:
        Dividend yield data for equity carry calculations.
    financing_rate:
        Financing rate applied in the carry signal.
    features:
        Feature matrix used for regime classification.
    regime_labels:
        Binary labels for training the regime model where ``1`` indicates risk-off.
    current_weights:
        Current portfolio weights.
    multipliers:
        Contract multipliers for each asset.
    fx_rates:
        FX rates to the base currency for each asset.
    capital:
        Total portfolio capital.
    margin_rates:
        Margin rates for each asset.
    returns:
        Historical return series for the assets.
    cost_estimates:
        Estimated execution costs indexed by time of day.
    var_limit:
        VaR limit used in the compliance report.
    band:
        No-trade band for turnover control.
    penalty:
        Fraction of trades to penalize when applying turnover control.
    target_vol:
        Target portfolio volatility for the ERC optimizer.

    Returns
    -------
    dict
        Dictionary containing intermediate and final results of the pipeline.
    """

    # 1. Data: construct continuous futures prices per asset
    prices_dict: Dict[str, pd.Series] = {}
    for asset, df in contract_data.groupby("asset"):
        cont = construct_continuous_futures(df)
        prices_dict[asset] = cont["back_adjusted"]
    prices = pd.DataFrame(prices_dict)

    # 2. Signals
    trend_signal = volatility_scaled_momentum(prices).iloc[-1]
    carry_signal = equity_carry(dividend_yield, financing_rate).iloc[-1]
    regime_model = train_logistic_regime_model(features, regime_labels)
    regime_prob = predict_regime_probability(features, regime_model).iloc[-1]
    raw_target = (trend_signal + carry_signal) / 2.0
    if raw_target.abs().sum() > 0:
        raw_target = raw_target / raw_target.abs().sum()
    raw_target *= 1.0 - float(regime_prob)

    # 3. Optimization with turnover control
    cov = returns.cov()
    erc_weights = erc(cov, target_vol=target_vol)
    target_weights = penalized_band_weights(erc_weights, current_weights, band, penalty)
    target_weights = target_weights.reindex(raw_target.index).fillna(0.0) * raw_target

    # 4. Risk checks
    portfolio_returns = returns @ target_weights
    var_value = calculate_var(portfolio_returns)
    margin = forecast_margin(target_weights * capital, margin_rates)
    cumulative = (1 + portfolio_returns).cumprod()
    drawdown = (cumulative.cummax() - cumulative).max()

    # 5. Execution
    latest_prices = prices.iloc[-1]
    target_contracts = weights_to_contracts(
        target_weights, latest_prices, multipliers, fx_rates, capital
    ).iloc[0]
    current_positions = weights_to_contracts(
        current_weights, latest_prices, multipliers, fx_rates, capital
    ).iloc[0]
    market_data = {
        "prices": latest_prices,
        "multipliers": multipliers,
        "fx_rates": fx_rates,
        "capital": capital,
        "spread": pd.Series(0.0, index=latest_prices.index),
        "volatility": returns.std(),
        "volume": contract_data.groupby("asset")["volume"].last(),
        "costs": cost_estimates,
        "days_to_expiry": (
            contract_data.groupby("asset")["expiry"].last()
            - contract_data.groupby("asset")["date"].last()
        ).dt.days,
    }
    schedule, slippage_costs = plan_orders(
        target_weights, current_positions, market_data
    )
    orders = target_contracts - current_positions

    # 6. Reporting
    report = generate_18f4_report(
        pd.Series(var_value, index=[prices.index[-1]]),
        pd.Series(target_weights.abs().sum(), index=[prices.index[-1]]),
        var_limit,
    )

    return {
        "prices": prices,
        "signals": {
            "trend": trend_signal,
            "carry": carry_signal,
            "regime_probability": regime_prob,
        },
        "weights": target_weights,
        "risk": {
            "var": var_value,
            "margin": margin,
            "drawdown": float(drawdown),
        },
        "orders": orders,
        "schedule": schedule,
        "slippage_costs": slippage_costs,
        "report": report,
    }


def main() -> None:
    """Command-line interface for running the daily pipeline."""
    parser = argparse.ArgumentParser(description="Run daily trading cycle")
    parser.add_argument("--dry-run", action="store_true", help="Run with mock data")
    args = parser.parse_args()

    if not args.dry_run:
        raise SystemExit("This CLI currently supports only --dry-run mode.")

    # Generate minimal mock data for demonstration purposes
    today = pd.Timestamp.today().normalize()
    dates = pd.date_range(today - pd.Timedelta(days=2), periods=3)
    contract_data = pd.DataFrame(
        {
            "asset": ["A"] * 3,
            "date": dates,
            "contract": ["A1"] * 3,
            "price": [100.0, 101.0, 102.0],
            "volume": [1000] * 3,
            "open_interest": [1000] * 3,
            "expiry": [today + pd.Timedelta(days=30)] * 3,
        }
    )
    dividend_yield = pd.DataFrame(0.02, index=dates, columns=["A"])
    features = pd.DataFrame({"ret": [0.0, 0.01, -0.005]}, index=dates)
    regime_labels = pd.Series([0, 0, 1], index=dates)
    current_weights = pd.Series({"A": 0.0})
    multipliers = pd.Series({"A": 1.0})
    fx_rates = pd.Series({"A": 1.0})
    margin_rates = pd.Series({"A": 0.1})
    returns = pd.DataFrame({"A": [0.0, 0.01, -0.005]}, index=dates)
    cost_estimates = pd.Series(
        [1.0, 2.0, 3.0], index=pd.date_range(today, periods=3, freq="H")
    )

    run_daily_cycle(
        contract_data=contract_data,
        dividend_yield=dividend_yield,
        financing_rate=0.01,
        features=features,
        regime_labels=regime_labels,
        current_weights=current_weights,
        multipliers=multipliers,
        fx_rates=fx_rates,
        capital=1_000_000.0,
        margin_rates=margin_rates,
        returns=returns,
        cost_estimates=cost_estimates,
        var_limit=0.2,
    )


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
