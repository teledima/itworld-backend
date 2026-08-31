
from django.db import models
from loguru import logger

from payments.models.project import Project


class ForbiddenTransition(Exception):
    pass


class InvoiceStatus(models.TextChoices):
    NEW = 'NEW'
    PENDING = 'PENDING'
    PAID = 'PAID'
    UNDERPAID = 'UNDERPAID'
    OVERPAID = 'OVERPAID'
    EXPIRED = 'EXPIRED'
    CANCELLED = 'CANCELLED'


fsm = {
    InvoiceStatus.NEW: frozenset([
        InvoiceStatus.PENDING,
        InvoiceStatus.PAID,
        InvoiceStatus.UNDERPAID,
        InvoiceStatus.OVERPAID,
        InvoiceStatus.EXPIRED,
        InvoiceStatus.CANCELLED,
    ]),
    InvoiceStatus.PENDING: frozenset([
        InvoiceStatus.PAID,
        InvoiceStatus.UNDERPAID,
        InvoiceStatus.OVERPAID,
        InvoiceStatus.EXPIRED,
        InvoiceStatus.CANCELLED,
    ]),
    InvoiceStatus.PAID: frozenset(),
    InvoiceStatus.UNDERPAID: frozenset([
        InvoiceStatus.PAID,
        InvoiceStatus.OVERPAID,
        InvoiceStatus.EXPIRED,
        InvoiceStatus.CANCELLED,
    ]),
    InvoiceStatus.OVERPAID: frozenset(),
    InvoiceStatus.EXPIRED: frozenset(),
    InvoiceStatus.CANCELLED: frozenset(),
}


class Invoice(models.Model):
    amount = models.DecimalField(max_digits=24, decimal_places=10)
    currency = models.CharField(max_length=3)
    status = models.CharField(choices=InvoiceStatus)
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    idempotency_key = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gte=10),
                name='min_amount_check'
            )
        ]

    def set_status(self, target: InvoiceStatus) -> None:
        if self.status != target and target not in fsm[self.status]:
            logger.bind(
                invoice_id=self.pk,
                status=self.status,
                target_status=target,
            ).error("Attempt to make broken transition")

            raise ForbiddenTransition

        self.status = target
