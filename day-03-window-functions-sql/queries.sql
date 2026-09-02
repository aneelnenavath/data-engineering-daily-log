-- Rank sales within each region, highest first
SELECT salesperson, region, amount,
       RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS rank
FROM sales;

-- Running total of all sales, ordered by date
SELECT sale_date, amount,
       SUM(amount) OVER (ORDER BY sale_date) AS running_total
FROM sales;

-- Compare each sale to the salesperson's previous sale
SELECT salesperson, sale_date, amount,
       LAG(amount) OVER (PARTITION BY salesperson ORDER BY sale_date) AS prev_amount
FROM sales;

-- Compare each sale to the salesperson's next sale
SELECT salesperson, sale_date, amount,
       LEAD(amount) OVER (PARTITION BY salesperson ORDER BY sale_date) AS next_amount
FROM sales;
