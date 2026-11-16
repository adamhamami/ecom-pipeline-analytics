# etl/extract.py
"""
Extract step:
- Read file paths from config/config.yaml
- Load CSVs from data/raw/
- Save them as Parquet files into data/processed/
"""

import pandas as pd
import yaml
from pathlib import Path


# ---------- Helper functions ----------

def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load YAML config and return as a Python dict."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def ensure_parent_dir(path_str: str) -> None:
    """Make sure the parent folder of a file path exists."""
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------- Main extract logic ----------

def extract_raw_to_processed() -> None:
    """
    Read raw CSVs (orders, order_items, customers)
    and save them as Parquet files in data/processed/.
    """
    config = load_config()

    raw_paths = config["data_paths"]
    processed_paths = config["processed_paths"]

    # Process each dataset in a simple loop
    for name in ["orders", "order_items", "customers"]:
        raw_path = raw_paths[name]
        processed_path = processed_paths[name]

        print(f"Reading {name} from {raw_path} ...")
        df = pd.read_csv(raw_path)

        print(f"✅ Loaded {len(df)} rows for {name}")

        # Make sure output folder exists
        ensure_parent_dir(processed_path)

        print(f"Writing {name} to {processed_path} (Parquet) ...")
        df.to_parquet(processed_path, index=False)

        print(f"✅ Finished {name}\n")


if __name__ == "__main__":
    extract_raw_to_processed()
    print("🎉 Extract step completed successfully.")