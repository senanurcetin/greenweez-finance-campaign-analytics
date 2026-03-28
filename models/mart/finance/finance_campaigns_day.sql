{{ config(materialized='view') }}

select
    fd.date_date as date,
    fd.operational_margin - coalesce(icd.ads_cost, 0) as ads_margin,
    fd.avg_basket as average_basket,
    fd.operational_margin,
    coalesce(icd.ads_cost, 0) as ads_cost,
    coalesce(icd.ads_impression, 0) as ads_impression,
    coalesce(icd.ads_clicks, 0) as ads_clicks,
    fd.total_quantity as quantity,
    fd.total_revenue as revenue,
    fd.total_purchase_cost as purchase_cost,
    fd.total_revenue - fd.total_purchase_cost as margin,
    fd.total_shipping_fee as shipping_fee,
    fd.total_log_cost as log_cost,
    fd.total_ship_cost as ship_cost
from {{ ref('finance_days') }} as fd
left join {{ ref('int_campaigns_day') }} as icd
    on fd.date_date = icd.date_date
order by date desc