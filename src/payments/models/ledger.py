from django.db import models
from django.db.models import Q
from payments.models import Merchant, Payment, Invoice, Project


class Ledger(models.Model):
    LedgerType = models.TextChoices("LedgerType", "FUND FEE")

    merchant = models.ForeignKey(Merchant, on_delete=models.RESTRICT)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    invoice = models.ForeignKey(Invoice, on_delete=models.RESTRICT, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.RESTRICT, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=4)
    type = models.CharField(choices=LedgerType)
    exchange_rate = models.DecimalField(max_digits=8, decimal_places=3)

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
