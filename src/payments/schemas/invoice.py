import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateInvoice(BaseModel):
    amount: Decimal = Field(max_digits=24, decimal_places=10, ge=10)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: uuid.UUID


class Invoice(BaseModel):
    id: int
    amount: Decimal = Field(max_digits=24, decimal_places=10, ge=10)
    currency: str = Field(min_length=3, max_length=3)
    status: str

    created_at: datetime
    expired_at: datetime


class InvoicePayment(BaseModel):
    id: int
    amount: Decimal = Field(max_digits=24, decimal_places=10)
    exchange_amount: Decimal = Field(max_digits=24, decimal_places=10)
    exchange_rate: Decimal = Field(max_digits=18, decimal_places=10)
    currency: str = Field(min_length=3, max_length=3)

    dt: datetime


class InvoiceDetailed(Invoice):
    paied: Decimal = Field(max_digits=24, decimal_places=10)
    payments: list[InvoicePayment]
