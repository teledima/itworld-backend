from functools import wraps
import json

from django.http import JsonResponse
from pydantic import BaseModel, ValidationError


def validate_body(schema: type[BaseModel], arg_name: str):
    """Декоратор для валидации JSON body через Pydantic."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"detail": "Invalid JSON format"}, 
                    status=400
                )

            try:
                validated_data = schema.model_validate(data)
            except ValidationError as e:
                # Формируем ответ в стиле FastAPI
                return JsonResponse(
                    {"detail": e.errors()}, 
                    status=422
                )

            kwargs[arg_name] = validated_data
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
