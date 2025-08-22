import pandas as pd
from typing import Optional


def construct_continuous_futures(
    data: pd.DataFrame,
    roll: str = "volume",
    days_before_expiry: Optional[int] = None,
) -> pd.DataFrame:
    """Create a continuous futures series with roll logic and price adjustments.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing contract data with the following columns:
        ``date``, ``contract``, ``price``, ``volume``, ``open_interest``, and ``expiry``.
        ``expiry`` should be constant for each contract.
    roll : {"volume", "oi"}, optional
        Trigger a roll when the next contract's volume or open interest exceeds
        the current front contract.  Ignored when ``days_before_expiry`` is set.
    days_before_expiry : int, optional
        If provided, roll to the next contract this many days before the current
        contract's expiry regardless of volume/Open Interest.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date with columns ``contract``, ``price``,
        ``back_adjusted`` and ``ratio_adjusted``.
    """

    if data.empty:
        return pd.DataFrame(columns=["contract", "price", "back_adjusted", "ratio_adjusted"])

    # Ensure required columns exist
    required = {"date", "contract", "price", "volume", "open_interest", "expiry"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = data.copy()
    df = df.sort_values(["date", "contract"]).reset_index(drop=True)

    contracts = df["contract"].unique()
    contract_data = {
        c: df[df["contract"] == c].set_index("date").sort_index()
        for c in contracts
    }
    expiries = {c: contract_data[c]["expiry"].iloc[0] for c in contracts}
    all_dates = sorted(df["date"].unique())

    active_contract: Optional[str] = None
    cumulative_diff = 0.0
    cumulative_ratio = 1.0
    records = []

    for date in all_dates:
        # determine current active contract
        if active_contract is None:
            available = [c for c in contracts if date in contract_data[c].index and date <= expiries[c]]
            if not available:
                continue
            active_contract = sorted(available, key=lambda c: expiries[c])[0]

        # find next contract candidate
        next_candidates = [
            c
            for c in contracts
            if expiries[c] > expiries[active_contract] and date in contract_data[c].index
        ]
        next_contract = (
            sorted(next_candidates, key=lambda c: expiries[c])[0]
            if next_candidates
            else None
        )

        roll_triggered = False
        if next_contract:
            if days_before_expiry is not None:
                if (expiries[active_contract] - date).days <= days_before_expiry:
                    roll_triggered = True
            if not roll_triggered and roll == "volume":
                vol_curr = contract_data[active_contract].loc[date, "volume"]
                vol_next = contract_data[next_contract].loc[date, "volume"]
                if vol_next > vol_curr:
                    roll_triggered = True
            if not roll_triggered and roll == "oi":
                oi_curr = contract_data[active_contract].loc[date, "open_interest"]
                oi_next = contract_data[next_contract].loc[date, "open_interest"]
                if oi_next > oi_curr:
                    roll_triggered = True
            if not roll_triggered and date > expiries[active_contract]:
                roll_triggered = True

        if roll_triggered and next_contract:
            price_old = contract_data[active_contract].loc[date, "price"]
            price_new = contract_data[next_contract].loc[date, "price"]
            diff = price_new - price_old
            ratio = price_new / price_old
            cumulative_diff += diff
            cumulative_ratio *= ratio
            active_contract = next_contract

        price = contract_data[active_contract].loc[date, "price"]
        record = {
            "date": date,
            "contract": active_contract,
            "price": price,
            "back_adjusted": price - cumulative_diff,
            "ratio_adjusted": price / cumulative_ratio,
        }
        records.append(record)

    result = pd.DataFrame(records).set_index("date")
    return result
