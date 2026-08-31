from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from payments.models import Invoice, InvoiceStatus
from payments.services.invoice import expire


class Command(BaseCommand):
    help = 'Expire invoice'

    def add_arguments(self, parser):
        parser.add_argument('merchant_ids', nargs='*', type=int)
        parser.add_argument('--dry-run', nargs='?', type=bool, default=False)

    @transaction.atomic
    def handle(self, *args, **options):
        invoices = Invoice.objects.filter(
            status__in=[
                InvoiceStatus.NEW,
                InvoiceStatus.PENDING,
                InvoiceStatus.UNDERPAID,
            ],
            expired_at__lt=datetime.now(tz=timezone.utc),
        ).only('id')

        if merchants := options.get('merchant_ids'):
            invoices = invoices.filter(
                project__merchant__in=merchants
            )

        if options.get('dry_run'):
            return 'invoices to expire: ' + ','.join([
                str(invoice.pk)
                for invoice
                in invoices.iterator(chunk_size=2000)
            ])

        for invoice in invoices.select_for_update().iterator(chunk_size=2000):
            expire(invoice)
