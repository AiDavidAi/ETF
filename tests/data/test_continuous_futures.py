import pandas as pd
import pathlib, sys
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from src.data.continuous_futures import construct_continuous_futures


def _sample_data_for_volume_roll():
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    data = []
    f1_prices = [100, 101, 102, 103, 104]
    f2_prices = [110, 111, 112, 113, 114]
    f1_vol = [200, 190, 180, 170, 160]
    f2_vol = [100, 210, 220, 230, 240]
    f1_oi = [1000, 900, 800, 700, 600]
    f2_oi = [500, 1100, 1200, 1300, 1400]
    for d, p1, p2, v1, v2, oi1, oi2 in zip(dates, f1_prices, f2_prices, f1_vol, f2_vol, f1_oi, f2_oi):
        data.append({'date': d, 'contract': 'F1', 'price': p1, 'volume': v1,
                     'open_interest': oi1, 'expiry': pd.Timestamp('2024-01-10')})
        data.append({'date': d, 'contract': 'F2', 'price': p2, 'volume': v2,
                     'open_interest': oi2, 'expiry': pd.Timestamp('2024-02-10')})
    return pd.DataFrame(data)


def _sample_data_for_expiry_roll():
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    data = []
    f1_prices = [100, 101, 102, 103, 104]
    f2_prices = [110, 111, 112, 113, 114]
    for d, p1, p2 in zip(dates, f1_prices, f2_prices):
        data.append({'date': d, 'contract': 'F1', 'price': p1, 'volume': 200,
                     'open_interest': 1000, 'expiry': pd.Timestamp('2024-01-05')})
        data.append({'date': d, 'contract': 'F2', 'price': p2, 'volume': 100,
                     'open_interest': 500, 'expiry': pd.Timestamp('2024-02-05')})
    return pd.DataFrame(data)


def test_volume_roll_back_and_ratio_adjustment():
    df = _sample_data_for_volume_roll()
    result = construct_continuous_futures(df, roll='volume')

    expected_contracts = ['F1', 'F2', 'F2', 'F2', 'F2']
    assert list(result['contract']) == expected_contracts

    # back adjusted series should match front contract path
    expected_prices = [100, 101, 102, 103, 104]
    assert list(result['back_adjusted']) == expected_prices

    ratio = 111 / 101
    expected_ratio = [100, 101] + [p / ratio for p in [112, 113, 114]]
    assert result['ratio_adjusted'].tolist() == pytest.approx(expected_ratio)


def test_open_interest_roll():
    df = _sample_data_for_volume_roll()
    result = construct_continuous_futures(df, roll='oi')

    expected_contracts = ['F1', 'F2', 'F2', 'F2', 'F2']
    assert list(result['contract']) == expected_contracts

    expected_prices = [100, 101, 102, 103, 104]
    assert list(result['back_adjusted']) == expected_prices

    ratio = 111 / 101
    expected_ratio = [100, 101] + [p / ratio for p in [112, 113, 114]]
    assert result['ratio_adjusted'].tolist() == pytest.approx(expected_ratio)


def test_days_before_expiry_roll():
    df = _sample_data_for_expiry_roll()
    result = construct_continuous_futures(df, roll='volume', days_before_expiry=2)

    expected_contracts = ['F1', 'F1', 'F2', 'F2', 'F2']
    assert list(result['contract']) == expected_contracts

    expected_prices = [100, 101, 102, 103, 104]
    assert list(result['back_adjusted']) == expected_prices

    ratio = 112 / 102
    expected_ratio = [100, 101, 102] + [p / ratio for p in [113, 114]]
    assert result['ratio_adjusted'].tolist() == pytest.approx(expected_ratio)
