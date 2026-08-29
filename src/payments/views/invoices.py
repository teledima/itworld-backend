from django.views.decorators.http import require_POST, require_GET
from django.http.response import JsonResponse, HttpResponse
from payments.decorators import validate_body
from payments.services.invoice import create_invoice, get_invoice_info, paied_amount
from payments.schemas.invoice import CreateInvoice, Invoice, InvoiceDetailed, InvoicePayment


@require_POST
@validate_body(CreateInvoice, 'invoice')
def create(request, invoice: CreateInvoice):
    invoice = create_invoice(request.auth, invoice)

    return JsonResponse(
        Invoice.model_validate(invoice, from_attributes=True).model_dump(),
    )


@require_GET
def get_by_id(request, id: int):
    invoice, ledgers = get_invoice_info(request.auth, id)

    detailed = InvoiceDetailed(
        id=invoice.id,
        amount=invoice.amount,
        paied=paied_amount(invoice),
        currency=invoice.currency,
        status=invoice.status,
        payments=[
            InvoicePayment(
                id=ledger.payment.id,
                amount=ledger.payment.amount,
                exchange_amount=ledger.amount,
                exchange_rate=ledger.exchange_rate,
                currency=ledger.payment.currency,
                dt=ledger.dt,
            )
            for ledger in ledgers
        ],
        created_at=invoice.created_at,
        expired_at=invoice.expired_at,
    )

    return JsonResponse(detailed.model_dump())


@require_POST
def cancel(request, id: int):
    return HttpResponse(status=204)
