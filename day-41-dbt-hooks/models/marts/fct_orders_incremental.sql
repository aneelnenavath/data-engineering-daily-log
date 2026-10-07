{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

select
    order_id,
    customer_id,
    amount,
    status
from {{ ref('stg_orders') }}

{% if is_incremental() %}
where order_id > (select max(order_id) from {{ this }})
{% endif %}
