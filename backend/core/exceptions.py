from django.db import IntegrityError
from logging_setup import logger_setup
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logger_setup()


class ValidationError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ошибка валидации."
    default_code = "validation_error"

    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    logger.error("Exception: %s %s", type(exc), exc)
    logger.debug("Response: %s", response)

    if response is None:
        response = Response(
            {"detail": "Произошла неизвестная ошибка."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        data = exc.detail if isinstance(exc.detail, dict) else {
            "detail": exc.detail}
        response = Response(data, status=exc.status_code)
    if isinstance(exc, IntegrityError):
        response = Response(
            {"detail": "Это поле должно быть уникальным."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, ParseError):
        response = Response(
            {
                "detail": "Ошибка чтения данных в формате JSON. "
                "Проверьте корректность."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return response
