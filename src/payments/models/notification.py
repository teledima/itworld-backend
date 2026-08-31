import uuid

from django.db import models

from payments.models.invoice import Invoice


class NotificationStatus(models.TextChoices):
    PENDING = 'PENDING'
    SENT = 'SENT'
    FAILED = 'FAILED'


class Notification(models.Model):
    idempotency_key = models.UUIDField(default=uuid.uuid4)
    invoice = models.ForeignKey(Invoice, on_delete=models.RESTRICT)
    status = models.CharField(
        choices=NotificationStatus,
        default=NotificationStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['status'])
        ]
