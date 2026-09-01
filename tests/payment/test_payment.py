import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import TestCase

from payments.models import (
    ExchangeRate,
    Invoice,
    InvoiceStatus,
    Ledger,
    LedgerType,
    Merchant,
    Payment,
    Project,
)
from payments.models.notification import Notification
from payments.schemas.payment import Payment as PaymentSchema
from payments.services.payment import process_payment


class ProccessPaymentCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.merchant = Merchant.objects.get(pk=1)
        cls.project = Project.objects.get(pk=1)
        cls.active_invoice = Invoice.objects.create(
            amount=Decimal('1000'),
            currency='RUB',
            status=InvoiceStatus.NEW,
            idempotency_key=uuid.uuid4(),
            project=cls.project,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )
        cls.terminated_invoice = Invoice.objects.create(
            amount=Decimal('1000'),
            currency='RUB',
            status=InvoiceStatus.CANCELLED,
            idempotency_key=uuid.uuid4(),
            project=cls.project,
            expired_at=datetime.now(tz=timezone.utc) + timedelta(days=1)
        )

        cls.usd_rub_exchange = ExchangeRate.objects.create(
            base_currency='USD',
            target_currency='RUB',
            rate=Decimal('80')
        )

    def test_success_flow(self):
        transaction_id = str(uuid.uuid4())
        schema = PaymentSchema(
            transaction_id=transaction_id,
            invoice_id=int(self.active_invoice.pk),
            currency='RUB',
            amount=Decimal('1000'),
        )

        process_payment(schema)

        payments = Payment.objects.filter(invoice=self.active_invoice)
        assert payments.count() == 1

        payment = payments.first()
        assert payment.amount == Decimal('1000')
        assert payment.currency == 'RUB'
        assert payment.transaction_id == transaction_id

        ledgers = Ledger.objects.filter(invoice=self.active_invoice)
        assert ledgers.count() == 2

        ledger_fund = ledgers.filter(type=LedgerType.FUND).first()
        ledger_fee = ledgers.filter(type=LedgerType.FEE).first()

        assert ledger_fund.amount == Decimal('1000')
        assert ledger_fund.exchange_rate == Decimal('1')
        assert ledger_fund.merchant == self.active_invoice.project.merchant
        assert ledger_fund.project == self.active_invoice.project
        assert ledger_fund.invoice == self.active_invoice
        assert ledger_fund.payment == payment

        assert ledger_fee.amount == Decimal('10')
        assert ledger_fee.exchange_rate == Decimal('1')
        assert ledger_fee.merchant == self.active_invoice.project.merchant
        assert ledger_fee.project == self.active_invoice.project
        assert ledger_fee.invoice == self.active_invoice
        assert ledger_fee.payment is None

        self.active_invoice.refresh_from_db()
        assert self.active_invoice.status == InvoiceStatus.PAID

        assert Notification.objects.filter(invoice=self.active_invoice).count() == 1

    def test_success_flow__retry(self):
        schema = PaymentSchema(
            transaction_id=str(uuid.uuid4()),
            invoice_id=int(self.active_invoice.pk),
            currency='RUB',
            amount=Decimal('1000'),
        )

        process_payment(schema)
        process_payment(schema)

        assert Payment.objects.filter(invoice=self.active_invoice).count() == 1
        assert Ledger.objects.filter(invoice=self.active_invoice).count() == 2

    def test_success_flow__partial_payment(self):
        schema = PaymentSchema(
            transaction_id=str(uuid.uuid4()),
            invoice_id=int(self.active_invoice.pk),
            currency='RUB',
            amount=Decimal('500'),
        )

        process_payment(schema)

        assert Payment.objects.filter(invoice=self.active_invoice).count() == 1
        assert Ledger.objects.filter(invoice=self.active_invoice).count() == 1

        self.active_invoice.refresh_from_db()
        assert self.active_invoice.status == InvoiceStatus.UNDERPAID

        ledger = Ledger.objects.filter(invoice=self.active_invoice).first()
        assert ledger.amount == Decimal('500')
        assert ledger.type == LedgerType.FUND

        assert Notification.objects.filter(invoice=self.active_invoice).count() == 0

    def test_success_flow__payment_in_another_currency(self):
        schema = PaymentSchema(
            transaction_id=str(uuid.uuid4()),
            invoice_id=int(self.active_invoice.pk),
            currency='USD',
            amount=Decimal('10'),
        )

        process_payment(schema)

        assert Payment.objects.filter(invoice=self.active_invoice).count() == 1
        assert Ledger.objects.filter(invoice=self.active_invoice).count() == 1

        ledger = Ledger.objects.filter(invoice=self.active_invoice).first()
        assert ledger.amount == Decimal('800')
        assert ledger.type == LedgerType.FUND
        assert ledger.exchange_rate == Decimal('80')

    def test_success_flow__payment_terminated(self):
        schema = PaymentSchema(
            transaction_id=str(uuid.uuid4()),
            invoice_id=int(self.terminated_invoice.pk),
            currency='USD',
            amount=Decimal('10'),
        )

        process_payment(schema)

        assert Payment.objects.filter(invoice=self.active_invoice).count() == 0
        assert Ledger.objects.filter(invoice=self.active_invoice).count() == 0
