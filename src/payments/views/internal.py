from django.views.decorators.http import require_POST
from django.http import HttpRequest, JsonResponse, HttpResponse
from loguru import logger
from payments.schemas.payment import Payment
from payments.decorators import validate_body
from payments.errors import HttpError
from payments.services.payment import process_payment


@require_POST
@validate_body(Payment, 'payment', enable_logging=True)
def payments(request: HttpRequest, payment: Payment):
    signature = request.headers.get('X-Signature')
    if not signature:
        logger.warning('Not found X-Signature in payment hook')
        return JsonResponse(
            status=401,
            data=HttpError(
                type='authentication_error',
                code='missing_required_header',
                message='Request is missing the required \'x-signature\' header',
            ).model_dump(),
        )

    process_payment(payment)
    
    return HttpResponse(status=204)
