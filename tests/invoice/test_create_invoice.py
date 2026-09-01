import uuid
from decimal import Decimal

from django.test import TestCase

from payments.models import Invoice, Project
from payments.schemas.invoice import CreateInvoice
from payments.services.invoice import create_invoice


class CreateInvoiceCase(TestCase):
    def test_create__default(self):
        project = Project.objects.get(pk=1)
        schema = CreateInvoice(
            amount=Decimal('1000'),
            currency='RUB',
            idempotency_key=uuid.uuid4(),
        )

        invoice = create_invoice(project, schema)

        assert invoice.pk == 1
        assert invoice.amount == Decimal('1000')
        assert invoice.currency == 'RUB'
        assert invoice.idempotency_key == schema.idempotency_key
        assert invoice.project == project

    def test_create__retry_return_same(self):
        project = Project.objects.get(pk=1)
        schema = CreateInvoice(
            amount=Decimal('1000'),
            currency='RUB',
            idempotency_key=uuid.uuid4(),
        )
        invoice1 = create_invoice(project, schema)
        invoice2 = create_invoice(project, schema)

        assert Invoice.objects.count() == 1
        assert invoice1 == invoice2
