select
    s.date_date,
    s.orders_id,
    s.products_id,
    s.revenue,
    s.quantity,
    p.purchase_price,
    sh.shipping_fee,
    sh.log_cost,
    sh.ship_cost,
    (s.quantity * p.purchase_price) as purchase_cost,
    (s.revenue - (s.quantity * p.purchase_price)) as margin,
    (s.revenue - (s.quantity * p.purchase_price) - sh.ship_cost - sh.log_cost) as operational_margin
from {{ ref('stg_raw__sales') }} as s
left join {{ ref('stg_raw__product') }} as p
    on s.products_id = p.products_id
left join {{ ref('stg_raw__ship') }} as sh
    on s.orders_id = sh.orders_id