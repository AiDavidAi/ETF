import os
import sys
import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from reporting import allocate_cayman


def test_allocate_cayman():
    w = pd.DataFrame({"ES": [0.5], "CL": [0.2]})
    domestic, cayman = allocate_cayman(w, ["CL"], limit=0.25)
    assert domestic.loc[0, "ES"] == 0.5
    assert domestic.loc[0, "CL"] == 0.0
    assert cayman.loc[0, "CL"] == 0.2
    assert cayman.loc[0, "ES"] == 0.0


def test_allocate_cayman_limit():
    w = pd.DataFrame({"CL": [0.3]})
    with pytest.raises(ValueError):
        allocate_cayman(w, ["CL"], limit=0.25)
