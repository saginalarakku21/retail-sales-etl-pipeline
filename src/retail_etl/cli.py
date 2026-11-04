"""Command-line ETL entry point."""
import argparse
import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from retail_etl.db import load, make_engine
from retail_etl.transform import transform

log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load retail CSV sales into PostgreSQL")
    parser.add_argument("--input", type=Path, default=Path("data/sample_sales.csv"))
    parser.add_argument("--rejects", type=Path, default=Path("data/rejected_rows.csv"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        parser.error("DATABASE_URL must be set (see .env.example)")
    raw = pd.read_csv(args.input, dtype={"order_id": "string", "customer_id": "string", "product_id": "string"})
    valid, rejected = transform(raw)
    if not rejected.empty:
        args.rejects.parent.mkdir(parents=True, exist_ok=True)
        rejected.to_csv(args.rejects, index=False)
        log.warning("Rejected %d invalid rows to %s", len(rejected), args.rejects)
    count = load(make_engine(url), valid)
    log.info("Loaded %d rows; rejected %d rows", count, len(rejected))


if __name__ == "__main__":
    main()
