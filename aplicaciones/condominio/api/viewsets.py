from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
## from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError

from drf_spectacular.utils import extend_schema

from domain.exceptions import RecursoDuplicadoError

from .serializers import (DefinirCuotaSerializer, DefinirCuotaResponseSerializer, CancelarCuotaSerializer, CancelarCuotaResponseSerializer
                          ,CobrarCuotaSerializer, CobrarCuotaResponseSerializer, ValidarCobroSerializer, ValidarCobroResponseSerializer
                          ,RegistrarTipoGastoSerializer, RegistrarTipoGastoResponseSerializer, ActualizarTipoGastoSerializer, ActualizarTipoGastoResponseSerializer
                          ,RegistrarSubTipoGastoSerializer, RegistrarSubTipoGastoResponseSerializer, ActualizarSubTipoGastoSerializer, ActualizarSubTipoGastoResponseSerializer
                          ,RegistrarProveedorSerializer, RegistrarProveedorResponseSerializer, ActualizarProveedorSerializer, ActualizarProveedorResponseSerializer
                          ,ActualizarSituacionProveedorSerializer, ActualizarSituacionProveedorResponseSerializer, RegistrarComentarioProveedorSerializer, RegistrarComentarioProveedorResponseSerializer
                          ,RegistrarGastoPagadoSerializer, RegistrarGastoPagadoResponseSerializer, CancelarGastoPagadoSerializer, CancelarGastoPagadoResponseSerializer
                          ,AutorizarGastoPagadoResponseSerializer, RegistrarComiteSerializer, RegistrarComiteResponseSerializer
                          ,TransferirAdministracionSerializer, TransferirAdministracionResponseSerializer, ModificarIntegrantesComiteSerializer, ModificarIntegrantesComiteResponseSerializer
                    )
from .use_cases import (DefinirCuotaUseCase, CancelarCuotaUseCase, CobrarCuotaUseCase, ValidarCobroUseCase, RegistrarTipoGastoUseCase, ActualizarTipoGastoUseCase
                        ,RegistrarSubTipoGastoUseCase, ActualizarSubTipoGastoUseCase, RegistrarProveedorUseCase, ActualizarProveedorUseCase
                        ,ActualizarSituacionProveedorUseCase, RegistrarComentarioProveedorUseCase, RegistrarGastoPagadoUseCase, CancelarGastoPagadoUseCase
                        ,AutorizarGastoPagadoUseCase
                        )

from .use_cases.comite import (RegistrarComiteUseCase, TransferirAdministracionUseCase, ModificarIntegrantesComiteUseCase

            )

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


class RegistrarTipoGasto(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=RegistrarTipoGastoSerializer,
        responses={201: RegistrarTipoGastoResponseSerializer},
        summary="Registrar Tipo Gasto ",
        description=(
            "Registrar tipo gasto "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarTipoGastoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = RegistrarTipoGastoUseCase.execute(
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
        response_serializer = RegistrarTipoGastoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ActualizarTipoGasto(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=ActualizarTipoGastoSerializer,
        responses={200: ActualizarTipoGastoResponseSerializer},
        summary="Actualizar Tipo Gasto ",
        description=(
            "Actualizar tipo gasto "            
        ),
    )

    def partial_update(self, request, *args, **kwargs):

        
        # 1. Validar los datos recibidos.
        serializer = ActualizarTipoGastoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = ActualizarTipoGastoUseCase.execute(
                administrador=request.user,
                tipo_gasto_id=kwargs['pk'],
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
        response_serializer = ActualizarTipoGastoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

class RegistrarSubTipoGasto(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=RegistrarSubTipoGastoSerializer,
        responses={201: RegistrarSubTipoGastoResponseSerializer},
        summary="Registrar Sub Tipo Gasto ",
        description=(
            "Registrar sub tipo gasto "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarSubTipoGastoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = RegistrarSubTipoGastoUseCase.execute(
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
        response_serializer = RegistrarSubTipoGastoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ActualizarSubTipoGasto(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=ActualizarSubTipoGastoSerializer,
        responses={200: ActualizarSubTipoGastoResponseSerializer},
        summary="Actualizar Sub Tipo Gasto ",
        description=(
            "Actualizar sub tipo gasto "            
        ),
    )

    def partial_update(self, request, *args, **kwargs):

        
        # 1. Validar los datos recibidos.
        serializer = ActualizarSubTipoGastoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = ActualizarSubTipoGastoUseCase.execute(
                administrador=request.user,
                sub_tipo_gasto_id=kwargs['pk'],
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
        response_serializer = ActualizarSubTipoGastoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class RegistrarProveedor(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=RegistrarProveedorSerializer,
        responses={201: RegistrarProveedorResponseSerializer},
        summary="Registrar Proveedor ",
        description=(
            "Registrar Proveedor "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarProveedorSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = RegistrarProveedorUseCase.execute(
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
        response_serializer = RegistrarProveedorResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ActualizarProveedor(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=ActualizarProveedorSerializer,
        responses={200: ActualizarProveedorResponseSerializer},
        summary="Actualizar proveedor ",
        description=(
            "Actualizar proveedor "            
        ),
    )

    def partial_update(self, request, *args, **kwargs):

        
        # 1. Validar los datos recibidos.
        serializer = ActualizarProveedorSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = ActualizarProveedorUseCase.execute(
                administrador=request.user,
                proveedor_id=kwargs['pk'],
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
        response_serializer = ActualizarProveedorResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class ActualizarSituacionProveedor(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=ActualizarSituacionProveedorSerializer,
        responses={200: ActualizarSituacionProveedorResponseSerializer},
        summary="Actualizar Situacion proveedor ",
        description=(
            "Actualizar Situacion proveedor "            
        ),
    )

    def partial_update(self, request, *args, **kwargs):

        
        # 1. Validar los datos recibidos.
        serializer = ActualizarSituacionProveedorSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = ActualizarSituacionProveedorUseCase.execute(
                administrador=request.user,
                proveedor_id=kwargs['pk'],
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
        response_serializer = ActualizarSituacionProveedorResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class RegistrarComentarioProveedor(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=RegistrarComentarioProveedorSerializer,
        responses={201: RegistrarComentarioProveedorResponseSerializer},
        summary="Registrar Comentario al Proveedor ",
        description=(
            "Registrar Comentario Proveedor "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarComentarioProveedorSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = RegistrarComentarioProveedorUseCase.execute(
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
        response_serializer = RegistrarComentarioProveedorResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class RegistrarGastoPagado(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=RegistrarGastoPagadoSerializer,
        responses={201: RegistrarGastoPagadoResponseSerializer},
        summary="Registrar Gasto Pagado ",
        description=(
            "Registrar Gasto Pagado "            
        ),
    )

    def create(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarGastoPagadoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = RegistrarGastoPagadoUseCase.execute(
                usuario=request.user,
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
        response_serializer = RegistrarGastoPagadoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CancelarGastoPagado(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'],
        request=CancelarGastoPagadoSerializer,
        responses={200: CancelarGastoPagadoResponseSerializer},
        summary="Cancelar Gasto Pagado",
        description=(
            "Cancelar Gasto Pagado"            
        ),
    )

    def partial_update(self, request, *args, **kwargs):

        
        # 1. Validar los datos recibidos.
        serializer = CancelarGastoPagadoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            # ejecutamos el caso de uso
            resultado = CancelarGastoPagadoUseCase.execute(
                administrador=request.user,
                gasto_pagado_id=kwargs['pk'],
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
        response_serializer = CancelarGastoPagadoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class AutorizarGastoPagado(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Gasto Pagado'], 
        request=None,       
        responses={200: AutorizarGastoPagadoResponseSerializer},
        summary="Autorizar Gasto Pagado",
        description=(
            "Autorizar Gasto Pagado"            
        ),
    )

    def partial_update(self, request, *args, **kwargs):
               
        try:
            # ejecutamos el caso de uso
            resultado = AutorizarGastoPagadoUseCase.execute(
                administrador=request.user,
                gasto_pagado_id=kwargs['pk']
                
            )

        except ValidationError as e:
            return Response(
                {
                    'detail': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Serializar la respuesta.
        response_serializer = AutorizarGastoPagadoResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

class RegistrarComite(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Comité'],
        request=RegistrarComiteSerializer,
        responses={201: RegistrarComiteResponseSerializer},
        summary="Registrar Comité",
        description=(
            "Registrar Comité"            
        ),
    )

    def create(self, request, *args, **kwargs):
    
            # 1. Validar los datos recibidos.
            serializer = RegistrarComiteSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
    
            # 2. Ejecutar el caso de uso.
            
            try:
                # ejecutamos el caso de uso
                resultado = RegistrarComiteUseCase.execute(
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
            response_serializer = RegistrarComiteResponseSerializer(
                resultado
            )
    
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )


class TransferirAdministracion(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Comité'],
        request=TransferirAdministracionSerializer,
        responses={200: TransferirAdministracionResponseSerializer},
        summary="Transferir Adminitración",
        description=(
            "Transferir Adminitración"            
        ),
        
    )

    def create(self, request):

        serializer = TransferirAdministracionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            resultado = TransferirAdministracionUseCase.execute(
                administrador_actual=request.user,
                **serializer.validated_data
            )

            response_serializer = (
                TransferirAdministracionResponseSerializer(
                    resultado
                )
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

class ModificarIntegrantesComite(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Comité'],
        request=ModificarIntegrantesComiteSerializer,
        responses={200: ModificarIntegrantesComiteResponseSerializer},
        summary="Modificar Integrantes Comite",
        description=(
            "Modificar Integrantes Comite"            
        ),
        
    )

    def create(self, request):

        serializer = ModificarIntegrantesComiteSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            resultado = ModificarIntegrantesComiteUseCase.execute(
                administrador=request.user,
                **serializer.validated_data
            )

            response_serializer = (
                ModificarIntegrantesComiteResponseSerializer(
                    resultado
                )
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )            
        