from django.views.decorators.http import require_POST, require_GET
from django.http.response import HttpResponse


@require_POST
def create(request):
    return HttpResponse(status=204)


@require_GET
def get_by_id(request, id: int):
    return HttpResponse(status=204)


@require_POST
def cancel(request, id: int):
    return HttpResponse(status=204)
