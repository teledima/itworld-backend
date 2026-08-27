from django.views.decorators.http import require_POST
from django.http.response import HttpResponse


@require_POST
def payments(request):
    return HttpResponse(status=204)