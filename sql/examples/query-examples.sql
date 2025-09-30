-- ================================================================
-- SQL Query Examples - Good vs Bad Practices
-- ================================================================
-- This file demonstrates common SQL patterns and their impact
-- on the quality analyzer score.
-- ================================================================

-- ----------------------------------------------------------------
-- EXAMPLE 1: Column Selection
-- ----------------------------------------------------------------

-- ❌ BAD: SELECT * (Score: -10 points)
-- Problem: Returns unnecessary columns, breaks when schema changes
SELECT * FROM users WHERE status = 'active';

-- ✅ GOOD: Explicit columns
-- Benefit: Clear intent, better performance, schema-change resistant
SELECT 
    id,
    username,
    email,
    created_at
FROM users 
WHERE status = 'active'
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 2: WHERE Clause Usage
-- ----------------------------------------------------------------

-- ❌ BAD: Missing WHERE (Score: -20 points)
-- Problem: Full table scan, returns all rows
SELECT id, name FROM products;

-- ✅ GOOD: Proper filtering
-- Benefit: Uses indexes, returns only needed data
SELECT 
    id, 
    name, 
    price 
FROM products 
WHERE category_id = 5 
    AND status = 'active'
ORDER BY price DESC
LIMIT 50;

-- ----------------------------------------------------------------
-- EXAMPLE 3: LIKE Patterns
-- ----------------------------------------------------------------

-- ❌ BAD: Leading wildcard (Score: -15 points)
-- Problem: Cannot use indexes, full scan required
SELECT * FROM customers 
WHERE email LIKE '%@gmail.com';

-- ⚠️  FAIR: Trailing wildcard (Score: -5 points)
-- Note: Can use index if column is indexed
SELECT 
    id,
    first_name,
    last_name,
    email
FROM customers 
WHERE last_name LIKE 'Smith%'
LIMIT 100;

-- ✅ GOOD: Exact match or full-text search
-- Benefit: Uses indexes efficiently
SELECT 
    id,
    first_name,
    last_name,
    email
FROM customers 
WHERE email = 'john.smith@example.com';

-- ----------------------------------------------------------------
-- EXAMPLE 4: Functions in WHERE Clause
-- ----------------------------------------------------------------

-- ❌ BAD: Function on column (Score: -15 points)
-- Problem: Prevents index usage (non-SARGable)
SELECT * FROM users 
WHERE UPPER(email) = 'ADMIN@EXAMPLE.COM';

-- ✅ GOOD: Function on value
-- Benefit: Index can be used
SELECT 
    id,
    username,
    email
FROM users 
WHERE email = LOWER('ADMIN@EXAMPLE.COM');

-- ✅ BETTER: Store normalized data
-- Benefit: No function needed at all
SELECT 
    id,
    username,
    email
FROM users 
WHERE email = 'admin@example.com';

-- ----------------------------------------------------------------
-- EXAMPLE 5: JOIN Best Practices
-- ----------------------------------------------------------------

-- ❌ BAD: Too many JOINs (Score: -10 points if > 6)
-- Problem: Complex execution plan, slow performance
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
JOIN categories cat ON p.category_id = cat.id
JOIN suppliers s ON p.supplier_id = s.id
JOIN warehouses w ON s.warehouse_id = w.id
JOIN regions r ON w.region_id = r.id
JOIN countries co ON r.country_id = co.id;

-- ✅ GOOD: Selective JOINs with aliases
-- Benefit: Only necessary tables, clear aliases
SELECT 
    o.id AS order_id,
    o.order_date,
    c.name AS customer_name,
    p.name AS product_name,
    o.quantity,
    o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
INNER JOIN products p ON o.product_id = p.id
WHERE o.order_date >= '2024-01-01'
    AND o.status = 'completed'
ORDER BY o.order_date DESC
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 6: Subquery vs JOIN
-- ----------------------------------------------------------------

-- ❌ BAD: NOT IN with subquery (Score: -10 points)
-- Problem: Slow with large datasets, NULL handling issues
SELECT * FROM users
WHERE id NOT IN (
    SELECT user_id FROM orders WHERE status = 'cancelled'
);

-- ✅ GOOD: LEFT JOIN with NULL check
-- Benefit: Better performance, handles NULLs correctly
SELECT 
    u.id,
    u.username,
    u.email
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'cancelled'
WHERE o.user_id IS NULL
LIMIT 1000;

-- ✅ BETTER: NOT EXISTS
-- Benefit: Stops at first match, optimal for NOT operations
SELECT 
    u.id,
    u.username,
    u.email
FROM users u
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.user_id = u.id 
        AND o.status = 'cancelled'
)
LIMIT 1000;

-- ----------------------------------------------------------------
-- EXAMPLE 7: LIMIT Clause
-- ----------------------------------------------------------------

-- ❌ BAD: Missing LIMIT (Score: -10 points)
-- Problem: Can return millions of rows unexpectedly
SELECT 
    id,
    name,
    email
FROM users
WHERE created_at > '2024-01-01';

-- ✅ GOOD: Always use LIMIT for safety
-- Benefit: Prevents accidental large result sets
SELECT 
    id,
    name,
    email
FROM users
WHERE created_at > '2024-01-01'
ORDER BY created_at DESC
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 8: Aggregate Functions
-- ----------------------------------------------------------------

-- ❌ BAD: SELECT * with aggregates (Score: -10 points)
-- Problem: Mixes detail and summary data incorrectly
SELECT *, COUNT(*) FROM orders GROUP BY customer_id;

-- ✅ GOOD: Explicit grouping columns
-- Benefit: Clear what's being aggregated
SELECT 
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_spent,
    AVG(total_amount) AS avg_order_value
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
HAVING COUNT(*) > 5
ORDER BY total_spent DESC
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 9: OR Conditions
-- ----------------------------------------------------------------

-- ❌ BAD: Multiple OR conditions (Score: -10 points if > 3)
-- Problem: Difficult to optimize, hard to read
SELECT * FROM products
WHERE category = 'Electronics'
   OR category = 'Computers'
   OR category = 'Software'
   OR category = 'Hardware'
   OR category = 'Accessories';

-- ✅ GOOD: Use IN clause
-- Benefit: Cleaner, more optimizable
SELECT 
    id,
    name,
    category,
    price
FROM products
WHERE category IN ('Electronics', 'Computers', 'Software', 'Hardware', 'Accessories')
    AND status = 'active'
ORDER BY price DESC
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 10: DISTINCT Usage
-- ----------------------------------------------------------------

-- ❌ BAD: DISTINCT with SELECT * (Score: -10 points)
-- Problem: Expensive operation on all columns
SELECT DISTINCT * FROM orders;

-- ⚠️  FAIR: DISTINCT on specific columns
-- Note: Consider if GROUP BY is more appropriate
SELECT DISTINCT 
    customer_id,
    order_date
FROM orders
WHERE order_date >= '2024-01-01'
LIMIT 100;

-- ✅ BETTER: Use GROUP BY when appropriate
-- Benefit: Can add aggregates, more explicit intent
SELECT 
    customer_id,
    DATE(order_date) AS order_date,
    COUNT(*) AS order_count
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id, DATE(order_date)
ORDER BY order_date DESC, order_count DESC
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 11: UNION vs UNION ALL
-- ----------------------------------------------------------------

-- ❌ BAD: UNION when duplicates don't matter (Score: -5 points)
-- Problem: Adds expensive DISTINCT operation
SELECT id, name FROM customers WHERE country = 'US'
UNION
SELECT id, name FROM customers WHERE country = 'CA';

-- ✅ GOOD: UNION ALL for better performance
-- Benefit: No duplicate removal overhead
SELECT 
    id, 
    name, 
    'US' AS country
FROM customers 
WHERE country = 'US'
UNION ALL
SELECT 
    id, 
    name, 
    'CA' AS country
FROM customers 
WHERE country = 'CA'
LIMIT 100;

-- ----------------------------------------------------------------
-- EXAMPLE 12: ORDER BY Best Practices
-- ----------------------------------------------------------------

-- ❌ BAD: ORDER BY without LIMIT (Score: -10 points)
-- Problem: Sorts entire result set unnecessarily
SELECT 
    id,
    name,
    price
FROM products
ORDER BY price DESC;

-- ✅ GOOD: ORDER BY with LIMIT
-- Benefit: Database can optimize with top-N sort
SELECT 
    id,
    name,
    price
FROM products
WHERE status = 'active'
ORDER BY price DESC
LIMIT 20;

-- ----------------------------------------------------------------
-- EXAMPLE 13: Complete Best Practice Example
-- ----------------------------------------------------------------

-- ✅ EXCELLENT: Combines all best practices
-- Score: 100/100
-- - Explicit columns
-- - Proper WHERE clause
-- - Appropriate JOINs with aliases
-- - No leading wildcards
-- - No functions on indexed columns
-- - Includes LIMIT
-- - Uses ORDER BY appropriately
SELECT 
    o.id AS order_id,
    o.order_number,
    o.order_date,
    c.name AS customer_name,
    c.email AS customer_email,
    p.name AS product_name,
    p.sku AS product_sku,
    o.quantity,
    o.unit_price,
    (o.quantity * o.unit_price) AS line_total
FROM orders o
INNER JOIN customers c 
    ON o.customer_id = c.id
INNER JOIN order_items oi 
    ON o.id = oi.order_id
INNER JOIN products p 
    ON oi.product_id = p.id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
    AND o.status = 'completed'
    AND c.country IN ('US', 'CA', 'UK')
    AND p.category_id = 5
ORDER BY o.order_date DESC, o.id DESC
LIMIT 100;

-- ================================================================
-- SUMMARY OF PENALTIES
-- ================================================================
-- SELECT *: -10 points
-- Missing WHERE clause: -20 points
-- Leading wildcard in LIKE: -15 points
-- Trailing wildcard in LIKE: -5 points
-- Function on column in WHERE: -15 points
-- More than 6 JOINs: -10 points
-- NOT IN with subquery: -10 points
-- Missing LIMIT: -10 points
-- More than 3 OR conditions: -10 points
-- DISTINCT with SELECT *: -10 points
-- UNION instead of UNION ALL: -5 points
-- ORDER BY without LIMIT: -10 points
-- ================================================================
