from decimal import Decimal

from pydantic import BaseModel, Field


class MechantBalance(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    total_amount: Decimal = Field()
