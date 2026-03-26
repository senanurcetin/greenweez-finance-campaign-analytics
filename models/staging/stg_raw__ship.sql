select
    cast(orders_id as int64) as orders_id,
    cast(shipping_fee as numeric) as shipping_fee,
    cast(shipping_fee_1 as numeric) as shipping_fee_1,
    cast(logCost as numeric) as log_cost,
    cast(ship_cost as numeric) as ship_cost
from {{ source('raw', 'ship') }}