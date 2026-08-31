from django.db import models
from django.db.models import Q

from payments.models.invoice import Invoice
from payments.models.merchant import Merchant
from payments.models.payment import Payment
from payments.models.project import Project


class LedgerType(models.TextChoices):
    FUND = 'FUND'
    FEE = 'FEE'


class Ledger(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.RESTRICT)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    invoice = models.ForeignKey(Invoice, on_delete=models.RESTRICT, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.RESTRICT, null=True)
    amount = models.DecimalField(max_digits=24, decimal_places=10)
    type = models.CharField(choices=LedgerType)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=10)

    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['invoice_id', 'type'],
                include=['amount'],
                name='ledger_invoice_id_type_idx',
            )
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='ledger_payment_amount_positive_check',
            )
        ]
