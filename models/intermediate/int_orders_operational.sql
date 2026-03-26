select
    o.orders_id,
    o.date_date,
    o.revenue,
    o.quantity,
    o.purchase_cost,
    o.margin,
    s.shipping_fee,
    s.log_cost,
    s.ship_cost,
    (o.margin + s.shipping_fee - s.log_cost - s.ship_cost) as operational_margin
from {{ ref('int_orders_margin') }} as o
left join {{ ref('stg_raw__ship') }} as s
    on o.orders_id = s.orders_id