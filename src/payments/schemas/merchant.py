from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class MechantBalance(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    total_amount: Decimal = Field()


class MerchantReportRequest(BaseModel):
    date_from: datetime
    date_to: datetime
    currency: str = Field(min_length=3, max_length=3)
    group_by: Literal['day', 'project']


class MerchantReport(BaseModel):
    group: str = Field(description='Значение поле группировки')
    payed_cnt: int = Field(description='Количество оплаченных счетов')
    total_cnt: int = Field(description='Количество выставленных счетов')
    all_invoice_amount: Decimal = Field(
        description='Сумма выставленная',
        max_digits=24,
        decimal_places=10,
    )
    fund_amount: Decimal = Field(
        description='Сумма фактически полученная',
        max_digits=24,
        decimal_places=10,
    )
    fee_amount: Decimal = Field(
        description='Сумма удержанной комиссии',
        max_digits=24,
        decimal_places=10,
    )
