from decimal import Decimal

from pydantic import BaseModel, Field


class Payment(BaseModel):
    transaction_id: str = Field(description='Идентификатор платежа в платёжной системе')
    invoice_id: int = Field(description='Идентификатор счета')
    currency: str = Field(min_length=3, max_length=3)
    amount: Decimal = Field(max_digits=24, decimal_places=10)
