import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from execution import process_ap_flows


def test_process_ap_flows():
    basket = pd.Series({"ES": 1, "NQ": 2})
    flows = process_ap_flows(3, 1, basket)
    expected = basket * 2
    pd.testing.assert_series_equal(flows, expected)
