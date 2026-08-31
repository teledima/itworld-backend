
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.decorators.http import require_GET
from pydantic import ValidationError

from payments.schemas.merchant import (
    MechantBalance,
    MerchantReport,
    MerchantReportRequest,
)
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
def report(request: HttpRequest, id: int):
    try:
        params = MerchantReportRequest(
            date_from=request.GET.get('date_from'),
            date_to=request.GET.get('date_to'),
            group_by=request.GET.get('group_by'),
            currency=request.GET.get('currency')
        )
    except ValidationError as e:
        return JsonResponse(
            {'detail': e.errors()},
            status=422,
        )
    else:
        report = merchant_svc.get_report(id, params)

        return JsonResponse(
            data=[
                MerchantReport(
                    group=str(row['group']),
                    payed_cnt=row['payed_cnt'],
                    total_cnt=row['total_cnt'],
                    all_invoice_amount=row['all_invoice_amount'],
                    fund_amount=row.get('fund_amount', 0),
                    fee_amount=row.get('fee_amount', 0),
                ).model_dump()
                for row in report
            ],
            safe=False,
        )
