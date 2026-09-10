# Day 8 — Join Strategy Comparison (MySQL, EXPLAIN)

## What this is

Three different SQL approaches to the same question -- "which customers
have never placed an order" -- run against Day 7's e-commerce schema, with
EXPLAIN used to see how MySQL actually executes each one rather than
assuming.

## Setup

Added more customers, orders, and order items to Day 7's schema so some
customers have orders and some genuinely have none -- Alice (1 order), Bob
(2), Carol (1), David and Emma (0 each). This is the exact scenario where
different join strategies matter.

## The three approaches

1. INNER JOIN + WHERE order_id IS NULL -- incorrect. INNER JOIN drops any
   customer with no matching order row before the WHERE clause runs, so
   the condition can never be true for a surviving row. Verified this
   directly: it returns an empty set every time, regardless of the real
   data, which is a dangerous kind of bug because it runs without error or
   warning.
2. LEFT JOIN + WHERE order_id IS NULL -- correct. Keeps every customer
   row and fills NULL into the orders columns when there is no match, so
   the IS NULL check means something real. Correctly returned David and
   Emma.
3. Correlated subquery with NOT EXISTS -- also correct, and a genuinely
   different way to ask the same question: for each customer row
   independently, does at least one matching order exist. Also correctly
   returned David and Emma.

## What EXPLAIN actually showed

Expected the LEFT JOIN and NOT EXISTS versions to have visibly different
execution plans. They did not. Both access customers with a full table
scan (type: ALL -- expected, nothing filters customers itself), then
access orders with an indexed lookup (type: ref, key: customer_id), and
both show "Not exists" in the Extra column. MySQL's optimizer recognises
LEFT JOIN ... WHERE x IS NULL and NOT EXISTS as logically the same
"antijoin" question and rewrites both into the same internal execution
strategy. The only difference between the two EXPLAIN outputs was a minor
"filtered" estimate, not a different strategy. Worth stating plainly
rather than assuming a textbook performance difference that the actual
EXPLAIN output does not support.

## Files

- queries.sql - all three approaches, commented
- README.md - this file

## How to run

docker start ecommerce-mysql
docker exec -it ecommerce-mysql mysql -uroot -pdevpassword ecommerce < queries.sql
