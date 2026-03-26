select
    cast(products_id as int64) as product_id,
    cast(purchse_PRICE as numeric) as purchase_price
from {{ source('raw', 'product') }}