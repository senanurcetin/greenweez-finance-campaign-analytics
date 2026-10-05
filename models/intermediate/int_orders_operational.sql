-- Orders without a shipping record (or with unpriced product lines) contribute 0
-- for the missing components instead of turning operational_margin into NULL,
-- which would silently drop the order from every daily/monthly total.
select
    o.orders_id,
    o.date_date,
    o.revenue,
    o.quantity,
    o.purchase_cost,
    o.margin,
    coalesce(s.shipping_fee, 0) as shipping_fee,
    coalesce(s.log_cost, 0) as log_cost,
    coalesce(s.ship_cost, 0) as ship_cost,
    (s.orders_id is not null) as has_ship_record,
    (
        coalesce(o.margin, 0)
        + coalesce(s.shipping_fee, 0)
        - coalesce(s.log_cost, 0)
        - coalesce(s.ship_cost, 0)
    ) as operational_margin
from {{ ref('int_orders_margin') }} as o
left join {{ ref('stg_raw__ship') }} as s
    on o.orders_id = s.orders_id
