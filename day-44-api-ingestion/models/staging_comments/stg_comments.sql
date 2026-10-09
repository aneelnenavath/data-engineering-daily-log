select
    id,
    post_id,
    name,
    email,
    body
from {{ ref('raw_comments') }}
