from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest

from payments.models import Project


class AuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path.startswith('/api'):
            api_key = request.headers.get('X-Api-Key')
            p = Project.objects.filter(api_key=api_key)

            if not api_key or len(p) == 0:
                raise PermissionDenied

            request.auth = p.get()

        response = self.get_response(request)

        return response
