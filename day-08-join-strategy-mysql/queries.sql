-- Day 8: Join strategy comparison
-- Question: which customers have never placed an order?

-- Approach 1: INNER JOIN -- INCORRECT for this question, kept here to
-- document why. INNER JOIN drops any customer with no matching order
-- row BEFORE the WHERE clause runs, so "o.order_id IS NULL" can never be
-- true for a surviving row. Always returns an empty set, regardless of
-- the real data.
SELECT c.name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Approach 2: LEFT JOIN -- correct. Keeps every customer row regardless
-- of a match, filling NULL into the orders columns when there is none.
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Approach 3: correlated subquery with NOT EXISTS -- also correct.
-- For each customer row, independently asks whether any matching order
-- exists.
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
