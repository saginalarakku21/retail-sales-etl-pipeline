import pandas as pd
import pytest
from retail_etl.transform import transform


def sample():
    return pd.DataFrame([
        {"order_id": "A1", "order_date": "2026-01-01", "customer_id": "C1", "product_id": "P1", "quantity": 2, "unit_price": 12.50},
        {"order_id": "A2", "order_date": "2026-01-02", "customer_id": "C2", "product_id": "P2", "quantity": -1, "unit_price": 5},
    ])


def test_valid_and_rejected():
    good, bad = transform(sample())
    assert len(good) == 1 and len(bad) == 1
    assert good.iloc[0]["total_amount"] == 25


def test_latest_duplicate_wins():
    df = pd.concat([sample().iloc[[0]], sample().iloc[[0]]], ignore_index=True)
    df.loc[1, "quantity"] = 3
    good, bad = transform(df)
    assert len(good) == 1 and len(bad) == 0
    assert good.iloc[0]["total_amount"] == 37.5


def test_missing_column():
    with pytest.raises(ValueError, match="Missing required columns"):
        transform(sample().drop(columns="order_id"))


def test_bad_dates_and_noninteger_quantity():
    df = sample().iloc[[0]].copy()
    df.loc[0, "order_date"] = "invalid"
    assert len(transform(df)[1]) == 1
    df.loc[0, "order_date"] = "2026-01-01"
    df.loc[0, "quantity"] = 1.5
    assert len(transform(df)[1]) == 1
