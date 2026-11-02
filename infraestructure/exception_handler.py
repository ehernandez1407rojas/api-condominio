# infrastructure/exception_handler.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from domain.exceptions import RecursoDuplicadoError


def custom_exception_handler(exc, context):
    # Primero dejamos que DRF maneje lo que ya sabe manejar
    response = exception_handler(exc, context)

    if isinstance(exc, RecursoDuplicadoError):
        return Response(
            {
                "error": "duplicado",
                "campo": exc.campo,
                "valor": exc.valor,
                "mensaje": exc.mensaje,
            },
            status=status.HTTP_409_CONFLICT,
        )

    return response