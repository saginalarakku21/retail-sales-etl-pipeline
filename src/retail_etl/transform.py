"""Pure, testable transformations and validation."""
import pandas as pd

REQUIRED = {"order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price"}


def transform(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (valid rows, rejected rows); latest duplicate order_id wins."""
    missing = REQUIRED - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    df = raw.copy()
    for col in ("order_id", "customer_id", "product_id"):
        df[col] = df[col].astype("string").str.strip()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", utc=True)
    for col in ("quantity", "unit_price"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    valid = (
        df["order_id"].notna() & df["order_id"].ne("")
        & df["customer_id"].notna() & df["customer_id"].ne("")
        & df["product_id"].notna() & df["product_id"].ne("")
        & df["order_date"].notna()
        & df["quantity"].notna() & df["quantity"].gt(0)
        & df["quantity"].mod(1).eq(0)
        & df["unit_price"].notna() & df["unit_price"].ge(0)
    ).fillna(False)
    rejected = df.loc[~valid].copy()
    clean = df.loc[valid].copy().drop_duplicates(subset=["order_id"], keep="last")
    clean["quantity"] = clean["quantity"].astype("int64")
    clean["unit_price"] = clean["unit_price"].round(2)
    clean["total_amount"] = (clean["quantity"] * clean["unit_price"]).round(2)
    return clean[["order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "total_amount"]], rejected
