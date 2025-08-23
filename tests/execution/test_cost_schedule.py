import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import generate_cost_aware_schedule


def test_generate_cost_aware_schedule_bias_to_low_cost():
    times = pd.date_range("2021-01-01 09:30", periods=3, freq="H")
    costs = pd.Series([5.0, 1.0, 10.0], index=times)
    sched = generate_cost_aware_schedule(100, costs)
    assert sched["quantity"].sum() == 100
    # middle slice has lowest cost, should receive the largest allocation
    assert sched.loc[sched["quantity"].idxmax(), "time"] == times[1]
