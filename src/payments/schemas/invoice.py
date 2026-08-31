from decimal import Decimal
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class CreateInvoice(BaseModel):
    amount: Decimal = Field(max_digits=16, decimal_places=4, ge=10)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: uuid.UUID


class Invoice(BaseModel):
    id: int
    amount: Decimal = Field(max_digits=16, decimal_places=4, ge=10)
    currency: str = Field(min_length=3, max_length=3)
    status: str

    created_at: datetime
    expired_at: datetime


class InvoicePayment(BaseModel):
    id: int
    amount: Decimal = Field(max_digits=16, decimal_places=4)
    exchange_amount: Decimal = Field(max_digits=16, decimal_places=4)
    exchange_rate: Decimal = Field(max_digits=8, decimal_places=3)
    currency: str = Field(min_length=3, max_length=3)

    dt: datetime


class InvoiceDetailed(Invoice):
    paied: Decimal = Field(max_digits=16, decimal_places=4)
    payments: list[InvoicePayment]
