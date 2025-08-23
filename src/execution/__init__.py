"""Execution utilities for translating signals into trade instructions."""

from .sizing import weights_to_contracts
from .twap import generate_twap_schedule
from .roll import roll_weights
from .slippage import estimate_slippage
from .ap import process_ap_flows

__all__ = [
    "weights_to_contracts",
    "generate_twap_schedule",
    "roll_weights",
    "estimate_slippage",
    "process_ap_flows",
]
