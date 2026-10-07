select
    shipment_id,
    destination,
    status,
    loaded_at
from {{ source('raw', 'raw_shipments') }}
