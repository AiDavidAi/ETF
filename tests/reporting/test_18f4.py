import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from reporting import generate_18f4_report


def test_generate_18f4_report():
    idx = pd.RangeIndex(2)
    var = pd.Series([0.08, 0.12], index=idx)
    exposure = pd.Series([0.9, 1.1], index=idx)
    report = generate_18f4_report(var, exposure, limit=0.1)
    assert report.loc[0, "breach"] is False
    assert report.loc[1, "breach"] is True
