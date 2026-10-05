-- Ad spend on days without orders must survive into the daily mart.
select
    (select sum(ads_cost) from {{ ref('int_campaigns_day') }}) as source_ads_cost,
    (select sum(ads_cost) from {{ ref('finance_campaigns_day') }}) as mart_ads_cost
where abs(
    (select sum(ads_cost) from {{ ref('int_campaigns_day') }})
    - (select sum(ads_cost) from {{ ref('finance_campaigns_day') }})
) > 0.5
