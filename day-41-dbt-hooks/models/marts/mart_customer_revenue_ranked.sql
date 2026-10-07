select
    customer_id,
    total_revenue,
    rank() over (order by total_revenue desc) as revenue_rank,
    dense_rank() over (order by total_revenue desc) as revenue_dense_rank,
    sum(total_revenue) over (
        order by total_revenue desc, customer_id asc
        rows between unbounded preceding and current row
    ) as running_total_revenue
from {{ ref('mart_customer_revenue') }}
