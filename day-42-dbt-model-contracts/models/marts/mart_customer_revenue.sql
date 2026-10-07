{{
    config(
        post_hook="insert into main.model_build_log (model_name, built_at, row_count) select '{{ this.name }}', current_timestamp, count(*) from {{ this }}"
    )
}}

select
    customer_id,
    count(order_id) as num_orders,
    sum(amount) as total_revenue
from {{ ref('stg_orders') }}
where status = 'completed'
group by customer_id
