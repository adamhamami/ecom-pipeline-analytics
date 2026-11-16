-- sql/marts.sql
-- Views for analytics / BI

-- 1) Daily KPIs: orders, GMV, net revenue, on-time rate
CREATE VIEW IF NOT EXISTS v_kpi_daily AS
SELECT
    DATE(order_date) AS order_date,
    COUNT(*) AS orders_count,
    SUM(gmv) AS gmv,
    SUM(net_revenue) AS net_revenue,
    AVG(on_time * 1.0) AS on_time_rate  -- 0–1; multiply by 100 in BI for %
FROM fact_orders
GROUP BY DATE(order_date);


-- 2) Revenue by channel and month
CREATE VIEW IF NOT EXISTS v_revenue_by_channel AS
SELECT
    channel,
    year_month,
    SUM(net_revenue) AS net_revenue,
    COUNT(*) AS orders_count
FROM fact_orders
GROUP BY channel, year_month;


-- 3) Average order value (AOV) by customer segment and month
CREATE VIEW IF NOT EXISTS v_aov_by_segment AS
SELECT
    c.segment,
    o.year_month,
    AVG(o.net_revenue) AS avg_order_value,
    COUNT(*) AS orders_count
FROM fact_orders o
JOIN dim_customer c
    ON o.customer_id = c.customer_id
GROUP BY c.segment, o.year_month;


-- 4) Shipping performance: average days to ship and late rate
CREATE VIEW IF NOT EXISTS v_ship_perf AS
SELECT
    year_month,
    AVG(days_to_ship * 1.0) AS avg_days_to_ship,
    AVG(
        CASE 
            WHEN on_time = 0 THEN 1.0
            ELSE 0.0
        END
    ) AS late_rate  -- 0–1; multiply by 100 in BI for %
FROM fact_orders
GROUP BY year_month;-- 4) Shipping performance: average days to ship and late rate
CREATE VIEW IF NOT EXISTS v_ship_perf AS
SELECT
    year_month,
    AVG(days_to_ship * 1.0) AS avg_days_to_ship,
    AVG(
        CASE 
            WHEN on_time = 0 THEN 1.0
            ELSE 0.0
        END
    ) AS late_rate  -- 0–1; multiply by 100 in BI for %
FROM fact_orders
GROUP BY year_month;-- 3) Average order value (AOV) by customer segment and month
CREATE VIEW IF NOT EXISTS v_aov_by_segment AS
SELECT
    c.segment,
    o.year_month,
    AVG(o.net_revenue) AS avg_order_value,
    COUNT(*) AS orders_count
FROM fact_orders o
JOIN dim_customer c
    ON o.customer_id = c.customer_id
GROUP BY c.segment, o.year_month;-- sql/marts.sql
-- Views for analytics / BI

-- 1) Daily KPIs: orders, GMV, net revenue, on-time rate
CREATE VIEW IF NOT EXISTS v_kpi_daily AS
SELECT
    DATE(order_date) AS order_date,
    COUNT(*) AS orders_count,
    SUM(gmv) AS gmv,
    SUM(net_revenue) AS net_revenue,
    AVG(on_time * 1.0) AS on_time_rate  -- 0–1; multiply by 100 in BI for %
FROM fact_orders
GROUP BY DATE(order_date);