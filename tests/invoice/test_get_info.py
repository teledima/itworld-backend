import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from django.test import TestCase

from payments.models import (
    Invoice,
    InvoiceStatus,
    Ledger,
    LedgerType,
    Merchant,
    Payment,
    Project,
)
from payments.services.invoice import get_invoice_info


class GetInvoiceInfoCase(TestCase):
    def test_info__default(self):
        project = Project.objects.get(pk=1)
        invoice = Invoice(
            amount=Decimal('1000'),
            currency='RUB',
            status=InvoiceStatus.PAID,
            idempotency_key=uuid.uuid4(),
            project=project,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )
        payment1 = Payment(
            amount=Decimal('450'),
            currency='RUB',
            invoice=invoice,
            transaction_id=uuid.uuid4(),
        )
        payment2 = Payment(
            amount=Decimal('550'),
            currency='RUB',
            invoice=invoice,
            transaction_id=uuid.uuid4(),
        )
        ledger1 = Ledger(
            merchant=project.merchant,
            project=project,
            invoice=invoice,
            payment=payment1,
            amount=Decimal('450'),
            type=LedgerType.FUND,
            exchange_rate=Decimal('1'),
        )
        ledger2 = Ledger(
            merchant=project.merchant,
            project=project,
            invoice=invoice,
            payment=payment2,
            amount=Decimal('550'),
            type=LedgerType.FUND,
            exchange_rate=Decimal('1'),
        )
        ledger_fee = Ledger(
            merchant=project.merchant,
            project=project,
            invoice=invoice,
            payment=None,
            amount=Decimal('10'),
            type=LedgerType.FEE,
            exchange_rate=Decimal('1'),
        )

        invoice.save()
        payment1.save()
        payment2.save()
        ledger1.save()
        ledger2.save()
        ledger_fee.save()

        invoice_info, ledgers = get_invoice_info(project, invoice.pk)

        assert invoice_info == invoice
        assert len(ledgers) == 2
        assert ledgers[0] == ledger2
        assert ledgers[1] == ledger1

    def test_info__invoice_without_payments(self):
        project = Project.objects.get(pk=1)
        invoice = Invoice(
            amount=Decimal('1000'),
            currency='RUB',
            status=InvoiceStatus.PAID,
            idempotency_key=uuid.uuid4(),
            project=project,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )
        invoice.save()

        invoice_info, ledgers = get_invoice_info(project, invoice.pk)

        assert invoice_info == invoice
        assert len(ledgers) == 0

    def test_info__invoice_from_another_project(self):
        merchant = Merchant.objects.get(pk=1)
        project = Project(
            name='project-2',
            api_key=uuid.uuid4(),
            webhook_url='http://some.host/hook',
            webhook_secret='secret',
            merchant=merchant
        )
        invoice = Invoice(
            amount=Decimal('1000'),
            currency='RUB',
            status=InvoiceStatus.PAID,
            idempotency_key=uuid.uuid4(),
            project=project,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )
        project.save()
        invoice.save()

        with pytest.raises(Invoice.DoesNotExist):
            get_invoice_info(Project.objects.get(pk=1), invoice.pk)
