# Data Dictionary –  E-Commerce Analytics Pipeline

This document describes the key datasets, tables, and fields used in the mini e-commerce analytics pipeline.

---

## 1. Source Files (`data/raw/`)

### 1.1 `orders.csv`

One row per **order**.

| Column               | Type    | Description                                                              |
|----------------------|---------|--------------------------------------------------------------------------|
| `order_id`           | int     | Unique identifier for the order.                                        |
| `order_date`         | date    | Date the order was placed.                                              |
| `customer_id`        | int     | References the customer who placed the order.                           |
| `channel`            | string  | Sales channel: e.g., `Web`, `Mobile`, `Marketplace`.                    |
| `status`             | string  | Order status: e.g., `Delivered`, `Shipped`, `Cancelled`.                |
| `subtotal`           | float   | Sum of item prices before discounts, shipping, and tax.                 |
| `shipping_fee`       | float   | Shipping cost charged for the order.                                    |
| `discount`           | float   | Discount applied to the order (e.g., promo codes).                      |
| `tax`                | float   | Tax amount applied to the order.                                        |
| `total`              | float   | Final total paid by the customer.                                       |
| `promised_ship_date` | date    | Date by which the order was promised to ship.                           |
| `actual_ship_date`   | date    | Date the order actually shipped.                                        |

### 1.2 `order_items.csv`

One row per **item** within an order.

| Column       | Type    | Description                                           |
|--------------|---------|-------------------------------------------------------|
| `order_id`   | int     | References the order this line item belongs to.      |
| `sku`        | string  | Product SKU (stock keeping unit).                     |
| `qty`        | int     | Quantity of this SKU in the order.                    |
| `unit_price` | float   | Price per unit of the SKU at time of purchase.       |
| `category`   | string  | Product category (e.g., `Apparel`, `Electronics`).   |

### 1.3 `customers.csv`

One row per **customer**.

| Column         | Type    | Description                                          |
|----------------|---------|------------------------------------------------------|
| `customer_id`  | int     | Unique identifier for the customer.                  |
| `signup_date`  | date    | Date the customer account was created.               |
| `city`         | string  | City of the customer.                                |
| `state`        | string  | State/region of the customer.                        |
| `segment`      | string  | Customer segment (e.g., `Consumer`, `SMB`).         |

---

## 2. Transformed Datasets (`data/processed/*_transformed.parquet`)

### 2.1 Orders – `orders_transformed.parquet`

Derived from `orders.csv` with additional business fields.

| Column              | Source            | Type    | Description                                                                 |
|---------------------|-------------------|---------|-----------------------------------------------------------------------------|
| `order_id`          | orders.csv        | int     | Unique order ID.                                                            |
| `order_date`        | orders.csv        | date    | Order placement date.                                                       |
| `customer_id`       | orders.csv        | int     | Customer placing the order.                                                |
| `channel`           | orders.csv        | string  | Sales channel.                                                              |
| `status`            | orders.csv        | string  | Original status text.                                                       |
| `subtotal`          | orders.csv        | float   | Item subtotal before discounts and tax.                                     |
| `shipping_fee`      | orders.csv        | float   | Shipping cost.                                                              |
| `discount`          | orders.csv        | float   | Discount amount.                                                            |
| `tax`               | orders.csv        | float   | Tax amount.                                                                 |
| `total`             | orders.csv        | float   | Final total.                                                                |
| `promised_ship_date`| orders.csv        | date    | Promised shipping date.                                                     |
| `actual_ship_date`  | orders.csv        | date    | Actual shipping date.                                                       |
| `gmv`               | derived           | float   | Gross Merchandise Value (here equal to `subtotal`).                         |
| `net_revenue`       | derived           | float   | Net revenue (here equal to `total`).                                        |
| `days_to_ship`      | derived           | int     | `actual_ship_date - order_date` in days.                                    |
| `on_time`           | derived           | bool/int| `True`/`1` if `actual_ship_date <= promised_ship_date`, else `False`/`0`.   |
| `year_month`        | derived           | string  | Year-month key in `YYYY-MM` format from `order_date`.                       |
| `status_normalized` | derived           | string  | Normalized status (trimmed + lowercased).                                   |

### 2.2 Order Items – `order_items_transformed.parquet`

Derived from `order_items.csv`.

| Column          | Source             | Type    | Description                                             |
|-----------------|--------------------|---------|---------------------------------------------------------|
| `order_id`      | order_items.csv    | int     | Order identifier.                                       |
| `sku`           | order_items.csv    | string  | Product SKU.                                            |
| `qty`           | order_items.csv    | int     | Quantity ordered.                                       |
| `unit_price`    | order_items.csv    | float   | Unit price.                                             |
| `category`      | order_items.csv    | string  | Product category.                                       |
| `extended_price`| derived            | float   | `qty * unit_price`.                                     |

### 2.3 Customers – `customers_transformed.parquet`

Derived from `customers.csv`.

| Column              | Source            | Type    | Description                                                 |
|---------------------|-------------------|---------|-------------------------------------------------------------|
| `customer_id`       | customers.csv     | int     | Customer ID.                                                |
| `signup_date`       | customers.csv     | date    | Signup date.                                               |
| `city`              | customers.csv     | string  | City.                                                       |
| `state`             | customers.csv     | string  | State.                                                      |
| `segment`           | customers.csv     | string  | Customer segment.                                           |
| `signup_year_month` | derived           | string  | Year-month of signup in `YYYY-MM` format.                   |

---

## 3. Data Warehouse Schema (`ecom_analytics.db`)

### 3.1 Dimension Tables

#### 3.1.1 `dim_customer`

One row per customer.

| Column              | Type    | Description                                          |
|---------------------|---------|------------------------------------------------------|
| `customer_id`       | int PK  | Unique customer ID.                                  |
| `signup_date`       | text    | Signup date (stored as text in SQLite).             |
| `city`              | text    | City.                                               |
| `state`             | text    | State.                                              |
| `segment`           | text    | Segment label.                                      |
| `signup_year_month` | text    | Year-month of signup (e.g., `2023-11`).            |

#### 3.1.2 `dim_date`

One row per distinct order date.

| Column       | Type    | Description                                  |
|--------------|---------|----------------------------------------------|
| `date_key`   | text PK | Date in `YYYY-MM-DD` format.                 |
| `year`       | int     | Calendar year.                               |
| `month`      | int     | Month number (1–12).                         |
| `day`        | int     | Day of month (1–31).                         |
| `year_month` | text    | Year-month key (e.g., `2024-01`).           |

#### 3.1.3 `dim_product`

One row per SKU.

| Column   | Type    | Description                              |
|----------|---------|------------------------------------------|
| `sku`    | text PK | Product SKU.                             |
| `category` | text  | Category of the product.                 |

---

### 3.2 Fact Tables

#### 3.2.1 `fact_orders`

One row per order.

| Column              | Type     | Description                                             |
|---------------------|----------|---------------------------------------------------------|
| `order_id`          | int PK   | Order ID.                                               |
| `order_date`        | text     | Date the order was placed.                              |
| `customer_id`       | int FK   | References `dim_customer.customer_id`.                  |
| `channel`           | text     | Sales channel.                                          |
| `status`            | text     | Original order status string.                           |
| `subtotal`          | real     | Item subtotal.                                          |
| `shipping_fee`      | real     | Shipping fee.                                           |
| `discount`          | real     | Discount amount.                                        |
| `tax`               | real     | Tax amount.                                             |
| `total`             | real     | Final total.                                            |
| `promised_ship_date`| text     | Promised ship date.                                     |
| `actual_ship_date`  | text     | Actual ship date.                                       |
| `gmv`               | real     | Gross Merchandise Value.                                |
| `net_revenue`       | real     | Net revenue figure.                                     |
| `days_to_ship`      | integer  | Days between order and actual ship date.                |
| `on_time`           | integer  | 1 if on time, 0 otherwise.                              |
| `year_month`        | text     | Year-month key for aggregation.                         |
| `status_normalized` | text     | Normalized order status (lowercase, trimmed).           |

#### 3.2.2 `fact_order_items`

One row per order line item.

| Column          | Type    | Description                                      |
|-----------------|---------|--------------------------------------------------|
| `order_id`      | int FK  | References `fact_orders.order_id`.              |
| `sku`           | text FK | References `dim_product.sku`.                   |
| `qty`           | integer | Quantity ordered.                               |
| `unit_price`    | real    | Price per unit.                                 |
| `category`      | text    | Product category.                               |
| `extended_price`| real    | `qty * unit_price`.                             |

---

## 4. Analytics Views (Marts)

### 4.1 `v_kpi_daily`

Grain: **one row per calendar date** (order_date).

| Column         | Description                                                    |
|----------------|----------------------------------------------------------------|
| `order_date`   | Date of orders.                                               |
| `orders_count` | Number of orders on that date.                                |
| `gmv`          | Total GMV for that date.                                      |
| `net_revenue`  | Total net revenue for that date.                              |
| `on_time_rate` | Average on-time rate (0–1); multiply by 100 for percentage.   |

### 4.2 `v_revenue_by_channel`

Grain: **channel + year_month**.

| Column         | Description                                   |
|----------------|-----------------------------------------------|
| `channel`      | Sales channel.                               |
| `year_month`   | Year-month key.                              |
| `net_revenue`  | Total net revenue for that channel & month.  |
| `orders_count` | Number of orders for that channel & month.   |

### 4.3 `v_aov_by_segment`

Grain: **segment + year_month**.

| Column           | Description                                                   |
|------------------|---------------------------------------------------------------|
| `segment`        | Customer segment from `dim_customer`.                         |
| `year_month`     | Year-month key.                                               |
| `avg_order_value`| Average order value (net_revenue) for that segment & month.   |
| `orders_count`   | Number of orders included in the calculation.                 |

### 4.4 `v_ship_perf`

Grain: **year_month**.

| Column             | Description                                               |
|--------------------|-----------------------------------------------------------|
| `year_month`       | Year-month key.                                           |
| `avg_days_to_ship` | Average shipping time in days.                            |
| `late_rate`        | Proportion of late orders (0–1); multiply by 100 in BI.   |
