#  E-Commerce Analytics Pipeline

A complete, end-to-end data engineering mini‑project demonstrating:

- Python ETL (extract → validate → transform → load)
- SQLite analytics warehouse (dims, facts, marts)
- Automated pipeline orchestration
- Data quality reporting + documentation
- BI-ready outputs for Power BI

This README is written exactly how you would place it into a `.md` file, including Markdown syntax.

---

## 1. Project Structure

```text
ecom-mini-pipeline/
  etl/
    extract.py
    validate.py
    transform.py
    load.py
    pipeline.py
  sql/
    schema.sql
    marts.sql
  bi/
  data/
    raw/
    processed/
  docs/
    README.md
    data_quality.md
    data_dictionary.md
  config/
    config.yaml
```

---

## 2. Tech Stack

- **Python**: pandas, sqlite3, PyYAML
- **Storage**: CSV → Parquet
- **Database**: SQLite (`ecom_analytics.db`)
- **Orchestration**: simple Python pipeline (`pipeline.py`)
- **BI**: Power BI (future step)
- **Config**: YAML-driven paths and settings

---

## 3. End‑to‑End Data Flow

### **1) Raw Data**
Input CSV files stored in `data/raw/`:
- `orders.csv`
- `order_items.csv`
- `customers.csv`

### **2) Extract (`extract.py`)**
- Reads raw CSVs  
- Saves canonical copies as Parquet in `data/processed/`

### **3) Validate (`validate.py`)**
- Required column checks  
- Total calculation validation  
- Date sanity checks  
- Duplicate filtering  
- Writes a basic data quality report to `docs/data_quality.md`

### **4) Transform (`transform.py`)**
Adds business‑ready features:
- `gmv`, `net_revenue`
- `days_to_ship`, `on_time`
- `year_month`
- `status_normalized`
- `extended_price` (on order_items)

### **5) Load (`load.py`)**
Creates and populates:
- `dim_customer`
- `dim_date`
- `dim_product`
- `fact_orders`
- `fact_order_items`

Database stored at:
```
data/processed/ecom_analytics.db
```

### **6) Marts (`marts.sql`)**
BI‑optimized views:
- `v_kpi_daily`
- `v_revenue_by_channel`
- `v_aov_by_segment`
- `v_ship_perf`

---

## 4. How to Run the Entire Pipeline

From the project root:

```bash
.venv\Scripts\activate
python etl/pipeline.py
```

Pipeline will:
- Extract CSV → Parquet  
- Validate and log data quality  
- Transform datasets  
- Load SQLite database  
- Rebuild dimensional model + fact tables  

---

## 5. Data Warehouse Tables

### **Dimension Tables**
- `dim_customer`
- `dim_date`
- `dim_product`

### **Fact Tables**
- `fact_orders`
- `fact_order_items`

### **Views (Analytics Marts)**
- `v_kpi_daily`
- `v_revenue_by_channel`
- `v_aov_by_segment`
- `v_ship_perf`

---

## 6. Inspecting the Database

You may use:
- **SQLTools + SQLite (Node)** extension in VS Code  
- **DB Browser for SQLite**  
- SQLite CLI

Example:
```sql
SELECT * FROM v_kpi_daily;
```

---

## 7. Future Enhancements

- Automated exports for Power BI
- Add dbt for documentation & testing
- Cloud warehouse (Azure SQL, Snowflake, Postgres)
- Add synthetic data generation using Faker
- Add S3/GCS ingestion options