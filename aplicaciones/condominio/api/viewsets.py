from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
## from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError

from drf_spectacular.utils import extend_schema

from .serializers import (DefinirCuotaSerializer, DefinirCuotaResponseSerializer, CancelarCuotaSerializer, CancelarCuotaResponseSerializer
                          ,CobrarCuotaSerializer, CobrarCuotaResponseSerializer, ValidarCobroSerializer, ValidarCobroResponseSerializer)
from .use_cases import (DefinirCuotaUseCase, CancelarCuotaUseCase, CobrarCuotaUseCase, ValidarCobroUseCase)

""" 
from ..models import Cuota, CuotaCobrada, TipoCuota, CuotaExigible
from rest_framework.decorators import action
from rest_framework import serializers

from datetime import datetime

from django.utils import timezone
from django.db import transaction
from .permissions import IsAdminOnly, IsAdminOrConserje
 """
# es el codigo defualt que salen todos los campos si validaciones
""" 
class CuotaViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    serializer_class = CuotaSerializer
    queryset = Cuota.objects.all()
 """

# utilizando los casos de uso

class DefinirCuota(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cuota'],
        request=DefinirCuotaSerializer,
        responses={201: DefinirCuotaResponseSerializer},
        summary="Definir cuota y las cuotas exigibles",
        description=(
            "Registra cuota para un condominio y las cuotas exigibles para los propietarios dentro de una única transacción."
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = DefinirCuotaSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            resultado = DefinirCuotaUseCase.execute(
                administrador=request.user,
                **serializer.validated_data
            )

        except ValidationError as e:
            return Response(
                {
                    'detail': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serializar la respuesta.
        response_serializer = DefinirCuotaResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

class CancelarCuota(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cuota'],
        request=CancelarCuotaSerializer,
        responses={201: CancelarCuotaResponseSerializer},
        summary="Cancelar cuota y las cuotas exigibles",
        description=(
            "Cancela una cuota y las cuotas exigibles futuras pendientes "
            "dentro de una única transacción."
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = CancelarCuotaSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            resultado = CancelarCuotaUseCase.execute(
                administrador=request.user,
                **serializer.validated_data
            )

        except ValidationError as e:
            return Response(
                {
                    'detail': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serializar la respuesta.
        response_serializer = CancelarCuotaResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CobrarCuota(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cuota'],
        request=CobrarCuotaSerializer,
        responses={201: CobrarCuotaResponseSerializer},
        summary="Cobrar cuota exigible",
        description=(
            "Cobra cuota exigible "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = CobrarCuotaSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            resultado = CobrarCuotaUseCase.execute(
                administrador_conserje=request.user,
                **serializer.validated_data
            )

        except ValidationError as e:
            return Response(
                {
                    'detail': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serializar la respuesta.
        response_serializer = CobrarCuotaResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
 

class ValidarCobro(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cuota'],
        request=ValidarCobroSerializer,
        responses={200: CobrarCuotaResponseSerializer},
        summary="Validar cobro de cuota ",
        description=(
            "Validar el cobro de una cuota "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = ValidarCobroSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = ValidarCobroUseCase.execute(
                administrador=request.user,
                **serializer.validated_data
            )

        except ValidationError as e:
            return Response(
                {
                    'detail': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serializar la respuesta.
        response_serializer = ValidarCobroResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )
