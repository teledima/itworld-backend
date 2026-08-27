from django.db import models
from payments.models.project import Project


class Invoice(models.Model):
    InvoiceStatus = models.TextChoices("InvoiceStatus", "NEW PENDING PAID UNDERPAID OVERPAID EXPIRED CANCELLED")

    amount = models.DecimalField(max_digits=16, decimal_places=4)
    currency = models.CharField(max_length=3)
    status = models.CharField(choices=InvoiceStatus)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    idempotency_key = models.CharField()

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(
                fields=('status', 'expired_at'),
                name='invoice_status_expired_at_idx',
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=('project', 'idempotency_key'),
                name='invoice_project_idempotency_key_key',
            )
        ]
