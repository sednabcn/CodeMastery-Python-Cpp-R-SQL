-- ================================================================
-- SQL PRACTICE TESTS - 30 QUESTIONS
-- ================================================================
-- Three difficulty levels: Beginner (10), Intermediate (10), Advanced (10)
-- Each question includes the task and expected quality considerations
-- ================================================================


-- ================================================================
-- LEVEL 1: BEGINNER (Questions 1-10)
-- ================================================================
-- Focus: Basic SELECT, WHERE, simple JOINs, basic filtering
-- ================================================================

-- ----------------------------------------------------------------
-- Question 1: Basic Column Selection
-- ----------------------------------------------------------------
-- Task: Write a query to retrieve the id, name, and email of all users
-- who have 'active' status. Return only the first 50 results.
-- 
-- Quality Requirements:
-- - Use explicit column names (no SELECT *)
-- - Include WHERE clause
-- - Include LIMIT clause
-- - Proper formatting
-- 
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 2: Simple Filtering
-- ----------------------------------------------------------------
-- Task: Get all products with a price greater than 100 and less than 500,
-- showing only id, name, and price. Limit to 25 results.
--
-- Quality Requirements:
-- - Explicit columns
-- - Proper range filtering
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 3: Exact Match Search
-- ----------------------------------------------------------------
-- Task: Find the customer with email 'john.doe@example.com'.
-- Return id, first_name, last_name, and email.
--
-- Quality Requirements:
-- - Use = operator (not LIKE)
-- - Explicit columns
-- - No need for LIMIT (looking for one specific record)
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 4: IN Clause Usage
-- ----------------------------------------------------------------
-- Task: Retrieve all orders with status 'pending', 'processing', or 'shipped'.
-- Show order_id, customer_id, status, and order_date. Limit to 100 results.
--
-- Quality Requirements:
-- - Use IN clause (not multiple OR conditions)
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 5: Simple ORDER BY
-- ----------------------------------------------------------------
-- Task: Get the 20 most expensive products showing id, name, and price.
-- Order by price from highest to lowest.
--
-- Quality Requirements:
-- - Proper ORDER BY with LIMIT
-- - Explicit columns
-- - Consider adding WHERE clause for active products
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 6: Date Filtering
-- ----------------------------------------------------------------
-- Task: Find all orders placed in the year 2024.
-- Show order_id, customer_id, order_date, and total_amount. Limit to 100.
--
-- Quality Requirements:
-- - Use BETWEEN or >= AND <= for date ranges
-- - Include LIMIT
-- - Explicit columns
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 7: Simple JOIN
-- ----------------------------------------------------------------
-- Task: List all orders with their customer names.
-- Show order_id, order_date, customer_name, and total_amount.
-- Limit to 50 results.
--
-- Quality Requirements:
-- - Use INNER JOIN with proper ON clause
-- - Use table aliases
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 8: COUNT with GROUP BY
-- ----------------------------------------------------------------
-- Task: Count how many orders each customer has made.
-- Show customer_id and order_count. Limit to 100 customers.
--
-- Quality Requirements:
-- - Use COUNT(*) with GROUP BY
-- - Explicit columns
-- - Include LIMIT
-- - Consider ORDER BY for most orders first
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 9: LIKE with Trailing Wildcard
-- ----------------------------------------------------------------
-- Task: Find all customers whose last name starts with 'Smith'.
-- Show id, first_name, last_name, and email. Limit to 50.
--
-- Quality Requirements:
-- - Use trailing wildcard (Smith%)
-- - NOT leading wildcard (%Smith)
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 10: Simple Aggregation
-- ----------------------------------------------------------------
-- Task: Calculate the total revenue (SUM of total_amount) from all completed orders
-- in 2024. Show just the total_revenue.
--
-- Quality Requirements:
-- - Use SUM() aggregate
-- - Filter by status and date
-- - Use alias for result
--
-- YOUR ANSWER HERE:




-- ================================================================
-- LEVEL 2: INTERMEDIATE (Questions 11-20)
-- ================================================================
-- Focus: Multiple JOINs, subqueries, HAVING, complex filtering
-- ================================================================

-- ----------------------------------------------------------------
-- Question 11: Multiple JOINs
-- ----------------------------------------------------------------
-- Task: Show order details with customer name and product name.
-- Include: order_id, order_date, customer_name, product_name, quantity, unit_price.
-- Only show completed orders from 2024. Limit to 100.
--
-- Quality Requirements:
-- - Use 3-4 JOINs maximum
-- - Clear table aliases
-- - Filter conditions in WHERE
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 12: GROUP BY with HAVING
-- ----------------------------------------------------------------
-- Task: Find customers who have placed more than 5 orders.
-- Show customer_id, customer_name, and order_count.
-- Order by order_count descending. Limit to 50.
--
-- Quality Requirements:
-- - Use GROUP BY with HAVING
-- - Include JOIN for customer name
-- - ORDER BY with LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 13: Subquery in WHERE
-- ----------------------------------------------------------------
-- Task: Find all products that have never been ordered.
-- Show product_id, name, and price. Limit to 100.
--
-- Quality Requirements:
-- - Use NOT EXISTS (not NOT IN)
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 14: LEFT JOIN with NULL Check
-- ----------------------------------------------------------------
-- Task: Find all customers who have NOT placed any orders.
-- Show customer_id, name, and email. Limit to 100.
--
-- Quality Requirements:
-- - Use LEFT JOIN
-- - Check for NULL in WHERE
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 15: CASE Statement
-- ----------------------------------------------------------------
-- Task: Categorize products by price range: 'Budget' (<50), 'Mid-range' (50-200),
-- 'Premium' (>200). Show product_id, name, price, and price_category.
-- Only show active products. Limit to 100.
--
-- Quality Requirements:
-- - Use CASE WHEN
-- - Include WHERE clause
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 16: Date Functions
-- ----------------------------------------------------------------
-- Task: Calculate each customer's total spending per month in 2024.
-- Show customer_id, month (as YYYY-MM), and total_spent.
-- Only include completed orders. Limit to 200.
--
-- Quality Requirements:
-- - Use date extraction functions appropriately
-- - GROUP BY customer and month
-- - Filter by date and status
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 17: Multiple Aggregates
-- ----------------------------------------------------------------
-- Task: For each product category, show: total_products, avg_price, 
-- min_price, max_price. Only include active products.
-- Order by total_products descending. Limit to 50.
--
-- Quality Requirements:
-- - Multiple aggregate functions
-- - GROUP BY category
-- - Include WHERE for filtering
-- - ORDER BY with LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 18: Self JOIN
-- ----------------------------------------------------------------
-- Task: Find all employees and their managers.
-- Show employee_id, employee_name, manager_id, manager_name.
-- Limit to 100.
--
-- Quality Requirements:
-- - Use self JOIN with clear aliases
-- - Handle employees with no manager (use LEFT JOIN)
-- - Explicit columns
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 19: UNION ALL
-- ----------------------------------------------------------------
-- Task: Combine all orders from 'US' customers and 'CA' customers into one result.
-- Show order_id, customer_id, country, and total_amount. Limit to 200.
--
-- Quality Requirements:
-- - Use UNION ALL (not UNION)
-- - Both queries should have same columns
-- - Include country identifier
-- - Include LIMIT at the end
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 20: Ranking with Window Functions
-- ----------------------------------------------------------------
-- Task: Show the top 3 most expensive products in each category.
-- Display category_id, product_id, product_name, and price.
--
-- Quality Requirements:
-- - Use ROW_NUMBER() or RANK() window function
-- - Partition by category
-- - Filter to top 3 per category
-- - No LIMIT needed (filtering in subquery)
--
-- YOUR ANSWER HERE:




-- ================================================================
-- LEVEL 3: ADVANCED (Questions 21-30)
-- ================================================================
-- Focus: Complex analytics, optimization, advanced aggregations
-- ================================================================

-- ----------------------------------------------------------------
-- Question 21: Running Total
-- ----------------------------------------------------------------
-- Task: Calculate the running total of order amounts for each customer,
-- ordered by order date. Show customer_id, order_id, order_date, 
-- order_amount, and running_total. Limit to customer_id = 123 for testing.
--
-- Quality Requirements:
-- - Use window function with proper PARTITION and ORDER
-- - Filter to specific customer
-- - Explicit columns
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 22: Complex Subquery with Aggregation
-- ----------------------------------------------------------------
-- Task: Find customers whose average order value is higher than the
-- overall average order value. Show customer_id, customer_name, 
-- avg_order_value. Limit to 50.
--
-- Quality Requirements:
-- - Subquery to calculate overall average
-- - GROUP BY for customer averages
-- - HAVING to filter
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 23: Pivot-like Query
-- ----------------------------------------------------------------
-- Task: Create a report showing total sales by month for each product category
-- in 2024. Show category_name, jan_sales, feb_sales, mar_sales, ..., dec_sales.
--
-- Quality Requirements:
-- - Use CASE WHEN with SUM for each month
-- - GROUP BY category
-- - Filter by year
-- - All months in one row per category
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 24: Cohort Analysis
-- ----------------------------------------------------------------
-- Task: Calculate customer retention by showing how many customers from
-- each registration month made purchases in subsequent months.
-- Show registration_month, customers_registered, customers_active_month_1,
-- customers_active_month_2, customers_active_month_3.
--
-- Quality Requirements:
-- - Multiple date comparisons
-- - Use COUNT DISTINCT appropriately
-- - GROUP BY registration period
-- - Complex JOIN conditions
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 25: Percentile Calculation
-- ----------------------------------------------------------------
-- Task: Find customers in the top 10% by total spending.
-- Show customer_id, customer_name, total_spent, and spending_percentile.
-- Limit to 100.
--
-- Quality Requirements:
-- - Use NTILE() or PERCENT_RANK() window function
-- - Calculate total spending per customer
-- - Filter to top percentile
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 26: Gap Analysis
-- ----------------------------------------------------------------
-- Task: Find gaps in order_id sequence (missing order numbers).
-- Show the missing order_id values. Assume order_id should be sequential.
--
-- Quality Requirements:
-- - Use LAG() or LEAD() window function or number series
-- - Identify gaps in sequence
-- - Return only missing IDs
-- - Efficient approach
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 27: Moving Average
-- ----------------------------------------------------------------
-- Task: Calculate 7-day moving average of daily order totals.
-- Show order_date, daily_total, and moving_avg_7day.
-- For the first 6 days, show available data average.
--
-- Quality Requirements:
-- - Window function with ROWS BETWEEN
-- - Daily aggregation first
-- - Proper date ordering
-- - Handle edge cases for first days
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 28: Complex EXISTS Condition
-- ----------------------------------------------------------------
-- Task: Find customers who have ordered products from at least 3 different
-- categories. Show customer_id, customer_name, and categories_count.
-- Limit to 100.
--
-- Quality Requirements:
-- - Use COUNT DISTINCT with proper JOINs
-- - GROUP BY with HAVING
-- - Efficient query structure
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 29: Recursive CTE (if supported)
-- ----------------------------------------------------------------
-- Task: Build an organizational hierarchy showing all employees under
-- a specific manager (manager_id = 5), including indirect reports.
-- Show employee_id, employee_name, manager_id, and level_depth.
--
-- Quality Requirements:
-- - Use recursive CTE
-- - Track hierarchy level
-- - Anchor and recursive members
-- - Limit depth if needed for safety
--
-- YOUR ANSWER HERE:




-- ----------------------------------------------------------------
-- Question 30: Advanced Analytics Query
-- ----------------------------------------------------------------
-- Task: Create a customer RFM (Recency, Frequency, Monetary) analysis.
-- For each customer show:
-- - customer_id, customer_name
-- - days_since_last_order (Recency)
-- - total_orders (Frequency)
-- - total_spent (Monetary)
-- - rfm_score (calculated as simple average of R, F, M quintiles)
-- Only include customers with at least one order. Limit to 100.
--
-- Quality Requirements:
-- - Multiple window functions (NTILE)
-- - Complex calculations
-- - Multiple JOINs and aggregations
-- - Date calculations
-- - Include LIMIT
--
-- YOUR ANSWER HERE:




-- ================================================================
-- ANSWER KEY - QUALITY SCORING CRITERIA
-- ================================================================
-- 
-- Each question will be scored on:
-- ✓ Explicit columns (not SELECT *)
-- ✓ Appropriate WHERE clause
-- ✓ Proper LIMIT usage
-- ✓ Efficient JOINs (< 6 tables)
-- ✓ No leading wildcards in LIKE
-- ✓ No functions on indexed columns in WHERE
-- ✓ Appropriate use of indexes
-- ✓ Clear aliases and formatting
-- ✓ Proper use of aggregation
-- ✓ Query optimization considerations
--
-- Beginner: Should score 80-100 points
-- Intermediate: Should score 70-100 points (more complexity allowed)
-- Advanced: Should score 60-100 points (trade-offs for functionality)
-- ================================================================

I've created a comprehensive SQL practice test with 30 questions across three difficulty levels:
📘 Level 1: Beginner (Questions 1-10)

Basic SELECT statements
Simple WHERE clauses
Single JOINs
Basic aggregations
ORDER BY and LIMIT

📗 Level 2: Intermediate (Questions 11-20)

Multiple JOINs
Subqueries
GROUP BY with HAVING
CASE statements
Window functions (intro)
UNION operations
Self JOINs

📕 Level 3: Advanced (Questions 21-30)

Running totals
Complex analytics
Moving averages
Cohort analysis
Percentile calculations
Gap analysis
Recursive CTEs
RFM analysis

Each question includes:

Clear task description
Quality requirements to follow
Space for answers
Expected best practices

The questions are designed to test not just SQL knowledge, but also query optimization and best practices as outlined in the original document. Students can practice writing queries that would score well on a quality analyzer!