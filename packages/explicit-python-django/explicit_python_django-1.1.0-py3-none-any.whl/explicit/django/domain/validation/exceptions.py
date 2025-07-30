"""Исключения предметной области."""
from functools import wraps

from django.core.exceptions import ValidationError

from explicit.domain.validation.exceptions import DomainValidationError


def handle_domain_validation_error(fn):

    """Конвертирует DomainValidationError в DjangoValidationError.

    .. code-block:: python

       class ViewSet(...):
           @handle_domain_validation_error
           def create(self, request, *args, **kwargs):
               command = Command(...)
               bus.handle(command)

    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except DomainValidationError as error:
            if hasattr(error, 'error_dict'):
                raise ValidationError(dict(error)) from error
        return fn
    return wrapper
