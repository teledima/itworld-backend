from django.db import DatabaseError
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from payments.decorators import validate_body
from payments.errors import HttpError
from payments.models.invoice import ForbiddenTransition, Invoice
from payments.schemas.invoice import CreateInvoice, InvoiceDetailed, InvoicePayment
from payments.schemas.invoice import Invoice as InvoiceSchema
from payments.services import invoice as invoice_svc


@require_POST
@validate_body(CreateInvoice, 'invoice')
def create(request, invoice: CreateInvoice):
    invoice = invoice_svc.create_invoice(request.auth, invoice)

    return JsonResponse(
        InvoiceSchema.model_validate(invoice, from_attributes=True).model_dump(),
    )


@require_GET
def get_by_id(request, id: int):
    try:
        invoice, ledgers = invoice_svc.get_invoice_info(request.auth, id)
    except Invoice.DoesNotExist:
        return HttpResponse(status=404)
    else:
        detailed = InvoiceDetailed(
            id=invoice.id,
            amount=invoice.amount,
            paied=invoice_svc.paied_amount(invoice),
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
    try:
        invoice_svc.cancel(request.auth, id)
    except Invoice.DoesNotExist:
        return HttpResponse(status=404)
    except DatabaseError:
        return JsonResponse(
            status=400,
            data=HttpError(
                type='bad_request',
                code='temporary_locked',
                message='you cannot cancel invoice while it is using'
            )
        )
    except ForbiddenTransition:
        return JsonResponse(
            status=400,
            data=HttpError(
                type='bad_request',
                code='forbidden_transition',
                message='invoice cannot be cancelled',
            ).model_dump()
        )

    return HttpResponse(status=204)
