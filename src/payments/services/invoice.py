from datetime import datetime, timezone, timedelta
from payments.schemas.invoice import CreateInvoice
from payments.models.invoice import Invoice
from payments.models.project import Project


def create_invoice(project: Project, invoice: CreateInvoice):
    invoices = Invoice.objects.filter(project_id=project.pk, idempotency_key=invoice.idempotency_key)

    if len(invoices) == 0:
        new_invoice = Invoice(
            amount=invoice.amount,
            currency=invoice.currency,
            status=Invoice.InvoiceStatus.NEW,
            project=project,
            idempotency_key=invoice.idempotency_key,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(minutes=10),
        )

        new_invoice.save()

    return invoices.get()
