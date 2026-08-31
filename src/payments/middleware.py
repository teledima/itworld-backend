from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest

from payments.models import Project


class AuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path.startswith('/api'):
            api_key = request.headers.get('X-Api-Key')
            if not api_key:
                raise PermissionDenied

            p = Project.objects.filter(api_key=api_key).first()
            if not p:
                raise PermissionDenied

            request.auth = p

        response = self.get_response(request)

        return response
