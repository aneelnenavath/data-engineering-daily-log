with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2026-01-01' as date)",
        end_date="cast('2027-01-01' as date)"
    ) }}
)

select
    date_day,
    {{ dbt_utils.generate_surrogate_key(['date_day']) }} as date_key,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day_of_month,
    extract(dow from date_day) as day_of_week,
    extract(dow from date_day) in (0, 6) as is_weekend
from spine
