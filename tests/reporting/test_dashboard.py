import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from reporting.dashboard import generate_dashboard


def test_generate_dashboard(tmp_path):
    portfolio = pd.DataFrame({"value": [100, 101]}, index=pd.date_range("2020-01-01", periods=2))
    var = 2.5
    out = tmp_path / "dash.csv"
    generate_dashboard(portfolio, var, out)
    assert out.exists()
    df = pd.read_csv(out, index_col=0)
    assert "VaR99_20d" in df.columns
    assert df["VaR99_20d"].iloc[0] == var
