select
    customer_id,
    count(order_id) as num_orders,
    sum(amount) as total_revenue
from {{ ref('stg_orders') }}
where status = 'completed'
group by customer_id
