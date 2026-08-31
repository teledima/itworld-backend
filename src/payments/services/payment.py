from datetime import datetime, timezone
from decimal import Decimal

from django.db import transaction
from loguru import logger

from payments.models import ExchangeRate, Invoice, InvoiceStatus, Ledger, Payment
from payments.schemas.payment import Payment as PaymentSchema
from payments.services.currency import exchange
from payments.services.invoice import paied_amount


@transaction.atomic
def process_payment(payment: PaymentSchema):
    payments = Payment.objects.filter(
        invoice_id=payment.invoice_id,
        transaction_id=payment.transaction_id,
    )

    if len(payments) > 0:
        return

    invoice = Invoice.objects.select_for_update().get(pk=payment.invoice_id)

    if (
        invoice.status in (
            InvoiceStatus.PAID,
            InvoiceStatus.OVERPAID,
            InvoiceStatus.EXPIRED,
            InvoiceStatus.CANCELLED,
        )
        or invoice.expired_at < datetime.now(tz=timezone.utc)
    ):
        logger.bind(
            invoice_id=invoice.pk,
            transaction_id=payment.transaction_id
        ).info('Invoice finished. Planning refund')
        # TODO: реализовать возврат средств
        return

    paied = paied_amount(invoice)
    exchanged_amount, rate = payment.amount, Decimal(1)

    if paied < invoice.amount:
        new_payment = Payment(
            amount=payment.amount,
            currency=payment.currency,
            invoice=invoice,
            transaction_id=payment.transaction_id,
        )
        exchanged_amount, rate = _exchange(payment, invoice)

        fund_ledger = Ledger(
            merchant=invoice.project.merchant,
            project=invoice.project,
            invoice=invoice,
            payment=new_payment,
            amount=exchanged_amount,
            exchange_rate=rate,
            type=Ledger.LedgerType.FUND,
        )

        new_payment.save()
        fund_ledger.save()

    amount_after_payment = paied_amount(invoice)
    if amount_after_payment >= invoice.amount:
        if amount_after_payment > invoice.amount:
            invoice.set_status(InvoiceStatus.OVERPAID)
        elif amount_after_payment == invoice.amount:
            invoice.set_status(InvoiceStatus.PAID)

        fee_ledger = Ledger(
            merchant=invoice.project.merchant,
            project=invoice.project,
            invoice=invoice,
            payment=None,
            amount=_calculate_fee(exchanged_amount),
            exchange_rate=1,
            type=Ledger.LedgerType.FEE,
        )
        fee_ledger.save()
    else:
        invoice.set_status(InvoiceStatus.UNDERPAID)

    invoice.save()


def _exchange(payment: PaymentSchema, invoice: Invoice) -> tuple[Decimal, Decimal]:
    if payment.currency == invoice.currency:
        return payment.amount, Decimal(1)

    try:
        rate = exchange(payment.currency, invoice.currency)
        return payment.amount * rate, rate
    except ExchangeRate.DoesNotExist:
        logger.bind(
            invoice_id=invoice.pk,
            invoice_currency=invoice.currency,
            payment_currency=payment.currency,
        ).error("Exchange rate not found")
        # TODO: добавить логику обработки

        raise


def _calculate_fee(amount: Decimal) -> Decimal:
    percentage_fee = amount * Decimal(0.01)
    return percentage_fee if percentage_fee > 0.5 else 0.5
