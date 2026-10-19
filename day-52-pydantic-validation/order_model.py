from typing import Literal

from pydantic import BaseModel, validator


class Order(BaseModel):
    order_id: int
    customer_id: int
    amount: float
    status: Literal["completed", "pending", "cancelled"]

    @validator("amount")
    def amount_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError("amount must be non-negative")
        return v
