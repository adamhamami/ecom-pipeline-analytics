# etl/pipeline.py
"""
Pipeline orchestrator:
Runs the full mini e-commerce analytics pipeline in order:

1) Extract  - read raw CSVs -> processed parquet
2) Validate - run data quality checks, log to docs/data_quality.md
3) Transform - add business-friendly derived columns
4) Load     - create/load SQLite dims & facts

Run from project root with:
    python etl/pipeline.py
"""

from extract import extract_raw_to_processed
from validate import run_validation
from transform import run_transforms
from load import run_load


def run_pipeline() -> None:
    print("====== STEP 1: EXTRACT ======")
    extract_raw_to_processed()

    print("\n====== STEP 2: VALIDATE ======")
    run_validation(save_report=True)

    print("\n====== STEP 3: TRANSFORM ======")
    run_transforms()

    print("\n====== STEP 4: LOAD ======")
    run_load()

    print("\n🎉 Full pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
