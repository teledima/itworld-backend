from django.db import models

from payments.models.invoice import Invoice


class Payment(models.Model):
    amount = models.DecimalField(max_digits=24, decimal_places=10)
    currency = models.CharField(max_length=3)
    invoice = models.ForeignKey(Invoice, on_delete=models.RESTRICT)
    transaction_id = models.CharField(unique=True)

    dt = models.DateTimeField(auto_now_add=True)
