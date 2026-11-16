# etl/validate.py
"""
Validation step:
- Validate processed parquet data (orders)
- Apply rules: required columns, dtypes, no negative values,
  total math checks, date sanity checks, duplicates
- Return cleaned dataframe + validation report
"""

import pandas as pd
import yaml
from pathlib import Path


# ---------- Load config ----------
def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------- Validation rules ----------
def validate_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {}

    # Required columns
    required = [
        "order_id", "order_date", "customer_id", "subtotal",
        "shipping_fee", "discount", "tax", "total", "status"
    ]
    report["missing_required_cols"] = [
        col for col in required if col not in df.columns
    ]
    if report["missing_required_cols"]:
        print("❌ Missing required columns:", report["missing_required_cols"])

    # Convert dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["promised_ship_date"] = pd.to_datetime(df["promised_ship_date"], errors="coerce")
    df["actual_ship_date"] = pd.to_datetime(df["actual_ship_date"], errors="coerce")

    # Remove nulls in key fields
    before = len(df)
    df = df.dropna(subset=["order_id", "order_date", "customer_id", "total", "status"])
    report["dropped_null_rows"] = before - len(df)

    # No negative totals
    before = len(df)
    df = df[df["total"] >= 0]
    report["removed_negative_total"] = before - len(df)

    # Total math check
    calc = (df["subtotal"] - df["discount"] + df["shipping_fee"] + df["tax"]).round(2)
    mismatches = calc.ne(df["total"].round(2)).sum()
    report["total_mismatch_count"] = mismatches

    # Keep only valid totals
    df = df[calc.eq(df["total"].round(2))]

    # Date sanity
    invalid_dates = df[df["actual_ship_date"] < df["order_date"]]
    report["invalid_ship_dates"] = len(invalid_dates)

    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    report["duplicate_orders_removed"] = before - len(df)

    return df, report


# ---------- Wrapper function ----------
def run_validation(save_report: bool = True) -> None:
    config = load_config()
    processed_paths = config["processed_paths"]

    print("🔍 Loading processed orders parquet...")
    df_orders = pd.read_parquet(processed_paths["orders"])

    # Validate
    cleaned_df, report = validate_orders(df_orders)

    print("\n📄 Validation Report:")
    for k, v in report.items():
        print(f"  {k}: {v}")

    # Save report to docs
    if save_report:
        save_path = Path("docs/data_quality.md")
        save_path.write_text("# Data Quality Report\n\n" + str(report))
        print(f"\n📝 Report saved to {save_path}")


if __name__ == "__main__":
    run_validation()
    print("\n🎉 Validation step completed.")
