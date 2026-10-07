{% snapshot customers_snapshot %}

{{
    config(
      target_schema='main',
      unique_key='customer_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

select * from {{ ref('raw_customers') }}

{% endsnapshot %}
