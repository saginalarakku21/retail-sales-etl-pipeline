# Retail Sales ETL Pipeline

Portfolio-ready Python + SQL pipeline: CSV ingestion → Pandas validation and deduplication → PostgreSQL transactional upsert → SQL analytics.

## Stack
Python 3.11+, Pandas, SQLAlchemy 2, psycopg 3, PostgreSQL 16, Docker Compose, pytest, Ruff, GitHub Actions.

## Run
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
docker compose up -d
retail-etl --input data/sample_sales.csv
pytest -q
ruff check src tests
docker compose exec -T postgres psql -U retail -d retail -f /dev/stdin < sql/analytics.sql
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Data contract
Required fields: order_id, order_date, customer_id, product_id, quantity, unit_price. IDs must be nonempty; dates parse as UTC; quantities must be positive whole numbers; prices nonnegative. Last duplicate order_id in a batch wins. Invalid records go to data/rejected_rows.csv (gitignored). Valid records are upserted with ON CONFLICT (order_id), making reruns idempotent.

## Architecture
```
Synthetic CSV → pandas extraction → validation + deduplication → PostgreSQL sales table → SQL analytics
                                       └── rejected rows CSV
```

## Portfolio talking points
- Idempotent loading with PostgreSQL primary keys and upserts.
- Transactional loads and database integrity constraints.
- Data quality quarantine for invalid rows.
- Automated unit tests and linting in GitHub Actions.
- SQL analytics for monthly revenue, top products, and repeat customers.

## Future enhancements
File-level audit logs, incremental watermarks, integration tests, Airflow orchestration, and Decimal-based money handling.

MIT licensed. Sample data is synthetic.