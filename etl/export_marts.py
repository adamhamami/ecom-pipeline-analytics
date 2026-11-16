# etl/export_marts.py

import sqlite3
import pandas as pd
from pathlib import Path

def export_view(db_path: str, view_name: str, output_path: str):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {view_name}", conn)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    conn.close()
    print(f"Exported {view_name} -> {output_path}")

def export_all():
    db = "data/processed/ecom_analytics.db"

    exports = {
        "v_kpi_daily": "data/processed/marts/v_kpi_daily.csv",
        "v_revenue_by_channel": "data/processed/marts/v_revenue_by_channel.csv",
        "v_aov_by_segment": "data/processed/marts/v_aov_by_segment.csv",
        "v_ship_perf": "data/processed/marts/v_ship_perf.csv",
    }

    for view, path in exports.items():
        export_view(db, view, path)

if __name__ == "__main__":
    export_all()
