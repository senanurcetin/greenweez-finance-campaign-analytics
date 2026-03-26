select
    cast(orders_id as int64) as orders_id,
    cast(shipping_fee as float64) as shipping_fee,
    cast(logCost as float64) as log_cost,
    cast(ship_cost as float64) as ship_cost
from {{ source('raw', 'ship') }}