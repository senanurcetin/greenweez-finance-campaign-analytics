select
    date_date,
    paid_source,
    campaign_key,
    campaign_name,
    ads_cost,
    impression,
    click
from {{ ref('stg_raw_adwords') }}

union all

select
    date_date,
    paid_source,
    campaign_key,
    campaign_name,
    ads_cost,
    impression,
    click
from {{ ref('stg_raw_bing') }}

union all

select
    date_date,
    paid_source,
    campaign_key,
    campaign_name,
    ads_cost,
    impression,
    click
from {{ ref('stg_raw_criterio') }}

union all

select
    date_date,
    paid_source,
    campaign_key,
    campaign_name,
    ads_cost,
    impression,
    click
from {{ ref('stg_raw_facebook') }}