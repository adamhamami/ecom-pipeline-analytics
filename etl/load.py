# etl/load.py
"""
Load step:
- Read transformed parquet files
- Create SQLite database with dimension + fact tables
- Insert rows (idempotent)
"""

import pandas as pd
import yaml
import sqlite3
from pathlib import Path


# ---------- Helpers ----------

def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_parent_dir(path_str: str) -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------- Table creation SQL ----------

SCHEMA_SQL = """
-- Dimension tables
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    signup_date TEXT,
    city TEXT,
    state TEXT,
    segment TEXT,
    signup_year_month TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    year_month TEXT
);

CREATE TABLE IF NOT EXISTS dim_product (
    sku TEXT PRIMARY KEY,
    category TEXT
);

-- Fact tables
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id INTEGER PRIMARY KEY,
    order_date TEXT,
    customer_id INTEGER,
    channel TEXT,
    status TEXT,
    subtotal REAL,
    shipping_fee REAL,
    discount REAL,
    tax REAL,
    total REAL,
    promised_ship_date TEXT,
    actual_ship_date TEXT,
    gmv REAL,
    net_revenue REAL,
    days_to_ship INTEGER,
    on_time INTEGER,
    year_month TEXT,
    status_normalized TEXT,
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id)
);

CREATE TABLE IF NOT EXISTS fact_order_items (
    order_id INTEGER,
    sku TEXT,
    qty INTEGER,
    unit_price REAL,
    category TEXT,
    extended_price REAL,
    FOREIGN KEY(order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY(sku) REFERENCES dim_product(sku)
);
"""


# ---------- Load Step ----------

def run_load() -> None:
    config = load_config()
    db_url = config["database"]["url"].replace("sqlite:///", "")
    ensure_parent_dir(db_url)

    print(f"📦 Connecting to SQLite database: {db_url}")
    conn = sqlite3.connect(db_url)
    cur = conn.cursor()

    print("📄 Creating tables...")
    cur.executescript(SCHEMA_SQL)
    conn.commit()

    # ----- Load transformed data -----
    print("📥 Reading transformed parquet files...")

    df_orders = pd.read_parquet("data/processed/orders_transformed.parquet")
    df_items = pd.read_parquet("data/processed/order_items_transformed.parquet")
    df_customers = pd.read_parquet("data/processed/customers_transformed.parquet")

    # ----- Insert dim_customer -----
    print("📌 Inserting into dim_customer...")
    df_customers.to_sql("dim_customer", conn, if_exists="replace", index=False)

    # ----- Insert dim_product (unique sku/category) -----
    print("📌 Inserting into dim_product...")
    df_products = df_items[["sku", "category"]].drop_duplicates()
    df_products.to_sql("dim_product", conn, if_exists="replace", index=False)

    # ----- Create dim_date from order_date -----
    print("📌 Creating dim_date...")
    df_dates = df_orders[["order_date"]].drop_duplicates()
    df_dates["order_date"] = pd.to_datetime(df_dates["order_date"])
    df_dates["date_key"] = df_dates["order_date"].dt.strftime("%Y-%m-%d")
    df_dates["year"] = df_dates["order_date"].dt.year
    df_dates["month"] = df_dates["order_date"].dt.month
    df_dates["day"] = df_dates["order_date"].dt.day
    df_dates["year_month"] = df_dates["order_date"].dt.to_period("M").astype(str)

    df_dates[["date_key", "year", "month", "day", "year_month"]].to_sql(
        "dim_date", conn, if_exists="replace", index=False
    )

    # ----- Insert fact_orders -----
    print("📌 Inserting into fact_orders...")
    df_orders.to_sql("fact_orders", conn, if_exists="replace", index=False)

    # ----- Insert fact_order_items -----
    print("📌 Inserting into fact_order_items...")
    df_items.to_sql("fact_order_items", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    print("🎉 Load step completed successfully!")


if __name__ == "__main__":
    run_load()
