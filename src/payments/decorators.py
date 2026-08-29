from functools import wraps
from loguru import logger
import json

from django.http import JsonResponse
from pydantic import BaseModel, ValidationError


def validate_body(schema: type[BaseModel], arg_name: str, enable_logging: bool = False):
    """Декоратор для валидации JSON body через Pydantic."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            validate_logger = logger
            if not enable_logging:
                validate_logger = validate_logger.add('/dev/null')

            with logger.contextualize(path=request.path):
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    logger.warning('Invalid JSON format')
                    return JsonResponse(
                        {'detail': 'Invalid JSON format'}, 
                        status=400
                    )

                try:
                    validated_data = schema.model_validate(data)
                except ValidationError as e:
                    errors = e.errors()
                    logger.bind(errors=errors).warning('invalid body')
                    return JsonResponse(
                        {'detail': errors}, 
                        status=422,
                    )

            kwargs[arg_name] = validated_data    
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
