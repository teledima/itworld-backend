from datetime import datetime, timezone, timedelta
from decimal import Decimal
from django.db.models import Sum
from payments.schemas.invoice import CreateInvoice
from payments.models.invoice import Invoice, InvoiceStatus
from payments.models.project import Project
from payments.models.ledger import Ledger


def create_invoice(project: Project, invoice: CreateInvoice):
    invoices = Invoice.objects.filter(project_id=project.pk, idempotency_key=invoice.idempotency_key)

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


def remain_amount(invoice: Invoice) -> Decimal:
    return Decimal(
        Ledger.objects
            .filter(invoice_id=invoice.pk, type=Ledger.LedgerType.FUND)
            .aggregate(Sum('amount', default=0))
            .get('amount__sum')
    )
