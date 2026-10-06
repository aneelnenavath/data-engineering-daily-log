{{
  config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='append'
  )
}}

select
    event_id,
    customer_id,
    event_type,
    amount,
    loaded_at
from {{ ref('raw_events') }}

{% if is_incremental() %}
where event_id > (select coalesce(max(event_id), 0) from {{ this }})
{% endif %}
