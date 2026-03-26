select
    cast(date_date as date) as date_date,
    cast(orders_id as int64) as orders_id,
    cast(pdt_id as int64) as product_id,
    cast(revenue as numeric) as revenue,
    cast(quantity as int64) as quantity
from {{ source('raw', 'sales') }}