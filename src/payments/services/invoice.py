from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from payments.models import Invoice, InvoiceStatus, Ledger, Notification, Project
from payments.schemas.invoice import CreateInvoice


def create_invoice(project: Project, invoice: CreateInvoice) -> Invoice:
    invoices = Invoice.objects.filter(
        project_id=project.pk,
        idempotency_key=invoice.idempotency_key,
    )

    if len(invoices) == 0:
        new_invoice = Invoice(
            amount=invoice.amount,
            currency=invoice.currency,
            status=InvoiceStatus.NEW,
            project=project,
            idempotency_key=invoice.idempotency_key,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(minutes=10),
        )

        new_invoice.save()

    return invoices.get()


def get_invoice_info(project: Project, id: int) -> tuple[Invoice, list[Ledger]]:
    invoice = Invoice.objects.get(pk=id, project_id=project.pk)
    ledgers = (
        invoice.ledger_set
            .order_by('-dt')
            .filter(payment__isnull=False, type=Ledger.LedgerType.FUND).all()
    )

    return invoice, ledgers


@transaction.atomic
def cancel(project: Project, id: int) -> None:
    invoice = (
        Invoice.objects
            .select_for_update(nowait=True)
            .get(pk=id, project_id=project.pk)
    )
    # TODO: логика для возврата платежей. создание заданий для джобы
    Notification(invoice=invoice).save()

    invoice.set_status(InvoiceStatus.CANCELLED)
    invoice.save()


def expire(invoice: Invoice) -> None:
    # TODO: логика для возврата платежей. создание заданий для джобы
    Notification(invoice=invoice).save()

    invoice.set_status(InvoiceStatus.EXPIRED)
    invoice.save()


def paied_amount(invoice: Invoice) -> Decimal:
    return Decimal(
        Ledger.objects
            .filter(invoice_id=invoice.pk, type=Ledger.LedgerType.FUND)
            .aggregate(Sum('amount', default=0))
            .get('amount__sum')
    )
