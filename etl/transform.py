# etl/transform.py
"""
Transform step:
- Read processed parquet files (orders, order_items, customers)
- Add business-friendly fields:
  - gmv, net_revenue
  - days_to_ship, on_time
  - year_month, status_normalized
  - extended_price on order_items
- Save transformed parquet files
"""

import pandas as pd
import yaml
from pathlib import Path


def load_config(path: str = "config/config.yaml") -> dict:
    """Load YAML config."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_parent_dir(path_str: str) -> None:
    """Make sure the parent folder of a file path exists."""
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns to orders dataframe."""

    # Make sure date columns are proper datetimes
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["promised_ship_date"] = pd.to_datetime(df["promised_ship_date"], errors="coerce")
    df["actual_ship_date"] = pd.to_datetime(df["actual_ship_date"], errors="coerce")

    # GMV (Gross Merchandise Value) – here we treat it as subtotal
    df["gmv"] = df["subtotal"]

    # Net revenue – here we’ll keep it simple and use total
    df["net_revenue"] = df["total"]

    # Days to ship
    df["days_to_ship"] = (df["actual_ship_date"] - df["order_date"]).dt.days

    # On-time flag: actual_ship_date <= promised_ship_date
    df["on_time"] = df["actual_ship_date"] <= df["promised_ship_date"]

    # Year-month for trending (e.g., "2024-01")
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)

    # Normalized status (lowercase, no extra spaces)
    df["status_normalized"] = df["status"].str.strip().str.lower()

    return df


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns to order_items dataframe."""
    # Extended price = qty * unit_price
    df["extended_price"] = df["qty"] * df["unit_price"]
    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple derived fields for customers."""
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df["signup_year_month"] = df["signup_date"].dt.to_period("M").astype(str)
    return df


def run_transforms() -> None:
    """Main function to run all transforms."""
    config = load_config()
    processed_paths = config["processed_paths"]

    # ----- Orders -----
    print("📦 Loading processed orders...")
    df_orders = pd.read_parquet(processed_paths["orders"])
    df_orders_tr = transform_orders(df_orders)

    orders_out = "data/processed/orders_transformed.parquet"
    ensure_parent_dir(orders_out)
    df_orders_tr.to_parquet(orders_out, index=False)
    print(f"✅ Saved transformed orders to {orders_out}")

    # ----- Order Items -----
    print("📦 Loading processed order_items...")
    df_items = pd.read_parquet(processed_paths["order_items"])
    df_items_tr = transform_order_items(df_items)

    items_out = "data/processed/order_items_transformed.parquet"
    ensure_parent_dir(items_out)
    df_items_tr.to_parquet(items_out, index=False)
    print(f"✅ Saved transformed order_items to {items_out}")

    # ----- Customers -----
    print("📦 Loading processed customers...")
    df_customers = pd.read_parquet(processed_paths["customers"])
    df_customers_tr = transform_customers(df_customers)

    customers_out = "data/processed/customers_transformed.parquet"
    ensure_parent_dir(customers_out)
    df_customers_tr.to_parquet(customers_out, index=False)
    print(f"✅ Saved transformed customers to {customers_out}")


if __name__ == "__main__":
    run_transforms()
    print("🎉 Transform step completed.")