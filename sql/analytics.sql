-- Monthly sales KPI
SELECT DATE_TRUNC('month', order_date)::date AS month,
       COUNT(*) AS orders,
       SUM(quantity) AS units_sold,
       SUM(total_amount) AS revenue
FROM sales
GROUP BY 1 ORDER BY 1;

-- Top products by revenue
SELECT product_id, COUNT(*) AS orders, SUM(total_amount) AS revenue
FROM sales GROUP BY product_id ORDER BY revenue DESC LIMIT 10;

-- Repeat customers
SELECT customer_id, COUNT(*) AS orders, SUM(total_amount) AS lifetime_value
FROM sales GROUP BY customer_id HAVING COUNT(*) > 1 ORDER BY lifetime_value DESC;
