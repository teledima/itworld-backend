from django.views.decorators.http import require_POST, require_GET
from django.http.response import JsonResponse, HttpResponse
from payments.decorators import validate_body
from payments.services.invoice import create_invoice
from payments.schemas.invoice import CreateInvoice, Invoice


@require_POST
@validate_body(CreateInvoice, 'invoice')
def create(request, invoice: CreateInvoice):
    invoice = create_invoice(request.auth, invoice)

    return JsonResponse(
        Invoice.model_validate(invoice, from_attributes=True).model_dump(),
    )


@require_GET
def get_by_id(request, id: int):
    return HttpResponse(status=204)


@require_POST
def cancel(request, id: int):
    return HttpResponse(status=204)
