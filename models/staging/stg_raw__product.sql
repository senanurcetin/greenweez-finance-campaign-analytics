select
    cast(products_id as int64) as products_id,
    cast(purchse_PRICE as float64) as purchase_price
from {{ source('raw', 'product') }}