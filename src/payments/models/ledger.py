from django.db import models
from django.db.models import Q
from payments.models.merchant import Merchant
from payments.models.payment import Payment


class Ledger(models.Model):
    LedgerType = models.TextChoices("LedgerType", "FUND FEE")

    merchant = models.ForeignKey(Merchant, on_delete=models.RESTRICT)
    amount = models.DecimalField(max_digits=12, decimal_places=4)
    type = models.CharField(choices=LedgerType)
    currency = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=8, decimal_places=3)
    payment = models.ForeignKey(Payment, on_delete=models.RESTRICT, null=True)

    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['merchant', 'dt'],
                name='ledger_merchant_dt_idx'
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='ledger_payment_amount_positive_check',
            )
        ]
