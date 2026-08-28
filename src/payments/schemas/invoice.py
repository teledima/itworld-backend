from decimal import Decimal
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class CreateInvoice(BaseModel):
    amount: Decimal = Field(max_digits=16, decimal_places=4)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: uuid.UUID = Field(...)


class Invoice(BaseModel):
    id: int = Field()
    amount: Decimal = Field(max_digits=16, decimal_places=4)
    currency: str = Field(min_length=3, max_length=3)
    status: str = Field(...)

    created_at: datetime
    expired_at: datetime
