from django.views.decorators.http import require_GET
from django.http.response import HttpResponse, JsonResponse
from payments.schemas.merchant import MechantBalance
from payments.services import merchant as merchant_svc


@require_GET
def balance(request, id: int):
    merchant_balance = merchant_svc.get_balance(id)

    return JsonResponse(
        [
            MechantBalance(
                currency=currency['currency'],
                total_amount=currency['total_amount'],
            ).model_dump()
            for currency in merchant_balance
        ],
        safe=False,
    )


@require_GET
def report(request, id: int):
    return HttpResponse(status=204)
