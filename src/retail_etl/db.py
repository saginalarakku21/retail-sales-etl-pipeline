"""PostgreSQL schema initialization and idempotent batch upserts."""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT PRIMARY KEY,
    order_date TIMESTAMPTZ NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(14, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(16, 2) NOT NULL CHECK (total_amount >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales(order_date);
"""
UPSERT = """
INSERT INTO sales (order_id, order_date, customer_id, product_id, quantity, unit_price, total_amount)
VALUES (:order_id, :order_date, :customer_id, :product_id, :quantity, :unit_price, :total_amount)
ON CONFLICT (order_id) DO UPDATE SET
    order_date = EXCLUDED.order_date,
    customer_id = EXCLUDED.customer_id,
    product_id = EXCLUDED.product_id,
    quantity = EXCLUDED.quantity,
    unit_price = EXCLUDED.unit_price,
    total_amount = EXCLUDED.total_amount,
    updated_at = NOW()
"""


def make_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def load(engine: Engine, df: pd.DataFrame) -> int:
    """Atomic batch upsert; reruns never duplicate order IDs."""
    rows = df.to_dict(orient="records")
    with engine.begin() as conn:
        for statement in SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))
        if rows:
            conn.execute(text(UPSERT), rows)
    return len(rows)
