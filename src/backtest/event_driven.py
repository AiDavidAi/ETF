import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


@dataclass
class EventDrivenBacktester:
    """Simple event-driven backtester supporting trades, rolls and slippage.

    Parameters
    ----------
    prices : pd.DataFrame
        DataFrame indexed by date with columns representing contract prices.
    multipliers : pd.Series
        Series mapping contract to dollar multiplier.
    slippage_bp : float, optional
        Slippage in basis points applied to each trade.  Positive numbers
        increase buy prices and decrease sell prices.  Default is ``0``.
    """

    prices: pd.DataFrame
    multipliers: pd.Series
    slippage_bp: float = 0.0
    cash: float = 0.0
    position: pd.Series = field(init=False)
    trades: List[Dict[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.position = pd.Series(0.0, index=self.prices.columns)
        self.slip = self.slippage_bp / 10_000.0

    def trade(self, date: pd.Timestamp, contract: str, quantity: float) -> None:
        price = self.prices.loc[date, contract]
        fill = price + price * self.slip * np.sign(quantity)
        self.cash -= quantity * fill * self.multipliers.get(contract, 1.0)
        self.position[contract] += quantity
        self.trades.append(
            {"date": date, "contract": contract, "qty": quantity, "price": fill}
        )

    def roll(self, date: pd.Timestamp, old: str, new: str) -> None:
        qty = self.position.get(old, 0.0)
        if qty != 0:
            self.trade(date, old, -qty)
            self.trade(date, new, qty)
            self.position[old] = 0.0

    def value(self, date: pd.Timestamp) -> float:
        val = self.cash
        for contract, qty in self.position.items():
            price = self.prices.loc[date, contract]
            val += qty * price * self.multipliers.get(contract, 1.0)
        return val

    def run(
        self,
        orders: Dict[pd.Timestamp, List[Tuple[str, float]]],
        rolls: Optional[Dict[pd.Timestamp, List[Tuple[str, str]]]] = None,
    ) -> pd.DataFrame:
        """Execute the backtest.

        Parameters
        ----------
        orders : dict
            Mapping date → list of (contract, quantity) to trade.
        rolls : dict, optional
            Mapping date → list of (old_contract, new_contract) specifying
            roll events.  Rolls are processed before any trades on the same day.

        Returns
        -------
        pd.DataFrame
            Portfolio value by date.
        """

        rolls = rolls or {}
        records = []
        for date in self.prices.index:
            for r in rolls.get(date, []):
                self.roll(date, r[0], r[1])
            for o in orders.get(date, []):
                self.trade(date, o[0], o[1])
            records.append({"date": date, "value": self.value(date)})
        return pd.DataFrame(records).set_index("date")
