SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;

-- a) Order totals
-- Expected: total_orders = 180, total_revenue = 99860.20,
-- avg_order_value = 554.78

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_revenue,
    ROUND(AVG(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS avg_order_value
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id;
-- b) COUNT(*) vs COUNT(rating)

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

-- c1) Customers with zero orders using LEFT JOIN
SELECT
    c.customer_id,
    c.name
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- c2) Customers with zero orders using NOT IN
SELECT
    customer_id,
    name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);

-- d) Return rate by city
SELECT
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(CASE WHEN o.returned = 1 THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(
        100.0 * SUM(CASE WHEN o.returned = 1 THEN 1 ELSE 0 END)
        / COUNT(o.order_id),
        1
    ) AS return_rate_pct
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- e1) Top 5 customers by total spend
SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_spend
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- e2) Customers ranked 3rd to 5th
SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_spend
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- f) Revenue and order count by category
SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(SUM(
        o.quantity * p.price *
        (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_revenue
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- g) Customers whose names start with A
SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY name;

-- h) Unique acquisition sources
SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;

SET SQL_SAFE_UPDATES = 0;

-- i1) Add loyalty_tier
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

-- i2) Assign loyalty tiers
UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

-- i3) Count customers by loyalty tier
SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
