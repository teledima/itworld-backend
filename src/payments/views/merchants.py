from django.views.decorators.http import require_GET
from django.http.response import HttpResponse


@require_GET
def balance(request, id: int):
    return HttpResponse(status=204)


@require_GET
def report(request, id: int):
    return HttpResponse(status=204)
