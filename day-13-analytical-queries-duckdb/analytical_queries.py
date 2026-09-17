import duckdb

con = duckdb.connect()

print("=== Rolling 7-day revenue (last 10 days shown) ===")
rolling = con.execute("""
    WITH daily AS (
        SELECT order_date, SUM(amount) AS daily_revenue
        FROM read_csv_auto('sales_data.csv')
        GROUP BY order_date
    )
    SELECT
        order_date,
        daily_revenue,
        ROUND(SUM(daily_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2) AS rolling_7day_revenue
    FROM daily
    ORDER BY order_date
""").df()
print(rolling.tail(10).to_string(index=False))

print("\n=== Top 5 customers by total revenue ===")
top_customers = con.execute("""
    SELECT customer_id, ROUND(SUM(amount), 2) AS total_revenue, COUNT(*) AS num_orders
    FROM read_csv_auto('sales_data.csv')
    GROUP BY customer_id
    ORDER BY total_revenue DESC
    LIMIT 5
""").df()
print(top_customers.to_string(index=False))

print("\n=== Month-over-month revenue growth ===")
mom = con.execute("""
    WITH monthly AS (
        SELECT date_trunc('month', order_date) AS month, SUM(amount) AS revenue
        FROM read_csv_auto('sales_data.csv')
        GROUP BY month
    )
    SELECT
        month,
        ROUND(revenue, 2) AS revenue,
        ROUND(
            100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month),
            1
        ) AS mom_growth_pct
    FROM monthly
    ORDER BY month
""").df()
print(mom.to_string(index=False))
