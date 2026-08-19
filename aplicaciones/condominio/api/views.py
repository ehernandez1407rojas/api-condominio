from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CustomTokenObtainPairSerializer, 
    UsuarioSerializer, 
    RegistrarCondominioSerializer, 
    RegistrarCondominioResponseSerializer,
    CambiarPasswordSerializer,
    PropiedadSerializer, CambiarPasswordResponseSerializer, CondominioSerializer, PaginationSerializer, CuotaCobradaSerializer,
    RegistrarPropietarioResponseSerializer, RegistrarPropietarioSerializer

)

from .use_cases import (RegistrarCondominioUseCase, CambiarPasswordUseCase, RegistrarPropietarioUseCase)
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import *


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegistrarCondominioView(APIView):

    @extend_schema(
        request=RegistrarCondominioSerializer,
        responses={201: RegistrarCondominioResponseSerializer},
        summary="Registrar condominio y usuario administrador",
        description=(
            "Registra un condominio junto con su primer usuario "
            "con rol ADMINISTRADOR dentro de una única transacción."
        ),
    )
    def post(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarCondominioSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        resultado = RegistrarCondominioUseCase.execute(
            **serializer.validated_data
        )

        # 3. Serializar la respuesta.
        response_serializer = RegistrarCondominioResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

class CambiarPasswordView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CambiarPasswordSerializer,
        responses={
        200: CambiarPasswordResponseSerializer
            },
        summary="Cambia el password de un usuario ya autenticado",
        description=(
            "Cambia el password de un usuario "
            ),
        )

    def post(self, request):

        serializer = CambiarPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            CambiarPasswordUseCase.execute(
                user=request.user,
                password_actual=serializer.validated_data['password_actual'],
                password_nueva=serializer.validated_data['password_nueva']
            )

        except ValidationError as e:
            return Response(
                e.message_dict,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'detail': 'La contraseña se cambió correctamente.'
            },
            status=status.HTTP_200_OK
        )    
    
class RegistrarUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar token para la respuesta
        token_serializer = CustomTokenObtainPairSerializer(data={
            'email_whatsapp': user.email_whatsapp,
            'password': request.data.get('password')
        })
        token_serializer.is_valid(raise_exception=True)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'user': serializer.data,
            'access': token_serializer.validated_data['access'],
            'refresh': token_serializer.validated_data['refresh']
        }, status=status.HTTP_201_CREATED, headers=headers)


class ListaCondominios(ListAPIView):
    ## queryset = Condominio.objects.all()
    serializer_class = CondominioSerializer
    pagination_class = PaginationSerializer
    
    def get_queryset(self):
        ## queryset = Condominio.objects.filter(nombre_corto='VIOLETA')
        queryset = Condominio.objects.listar_condominios_nombre('VIOLE')
        return queryset
        
class FiltroCondominio(ListAPIView):
    ## queryset = Condominio.objects.all()
    serializer_class = CondominioSerializer
    
    def get_queryset(self):
        print('*******')
        condominio = self.kwargs['condominio']
        print (f'condominio a buscar: {condominio}')
        
        ## queryset = Condominio.objects.filter(nombre_corto='VIOLETA')
        queryset = Condominio.objects.listar_condominios_por_nombre(condominio)
        return queryset        
    
class CondominioPorFolio(ListAPIView):
    ## queryset = Condominio.objects.all()
    serializer_class = CondominioSerializer    
    
    def get_queryset(self):
        print('*******')
        folio = self.kwargs['folio']
        print (f'condominio a buscar por folio : {folio}')                
        queryset = Condominio.objects.condominio_por_folio(folio)
        return queryset   
    
class PropiedadesPorFecha(ListAPIView):
    serializer_class = PropiedadSerializer
    pagination_class = PaginationSerializer
    
    def get_queryset(self):
        anio = self.kwargs['anio']
        queryset = Propiedad.objects.lista_propiedades_posteriores(anio)
        return queryset
    
class PropiedadPorPropietario(ListAPIView):
    serializer_class = PropiedadSerializer
    
    def get_queryset(self):
        propietario = self.request.query_params.get('propietario', '')
        return Propiedad.objects.propiedades_por_propietario(propietario)
    
class PropiedadPorPropietarioYCondominio(ListAPIView):
    serializer_class = PropiedadSerializer
    pagination_class = PaginationSerializer

    def get_queryset(self):
        propietario = self.request.query_params.get('propietario', '')
        condominio = self.request.query_params.get('condominio')

        return Propiedad.objects.propiedades_por_propietario_y_condominio(
            propietario,
            condominio
        )
    
class PropiedadDetalle(RetrieveAPIView):    
    serializer_class = PropiedadSerializer
    queryset = Propiedad.objects.all()
        
        
class CuotaCobradaGuardar(CreateAPIView):
    serializer_class = CuotaCobradaSerializer
    queryset = CuotaCobrada.objects.all()
    
class PropiedadCreateAPIView(CreateAPIView):
    serializer_class = PropiedadSerializer
    queryset = Propiedad.objects.all()
    
class PropiedadUpdateAPIView(UpdateAPIView):
    serializer_class = PropiedadSerializer
    queryset = Propiedad.objects.all()

      

@extend_schema(
    request=CondominioSerializer,
    responses=CondominioSerializer,
)    
class CondominioCreateAPIView(CreateAPIView):
    serializer_class = CondominioSerializer
    queryset = Condominio.objects.all()
    
class CondominioUpdateAPIView(UpdateAPIView):
    serializer_class = CondominioSerializer
    queryset = Condominio.objects.all()    


class RegistrarPropietarioView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RegistrarPropietarioSerializer,
        responses={201: RegistrarPropietarioResponseSerializer},
        summary="Registrar propietario y propiedad",
        description=(
            "Registra una propiedad junto con su usuario propietario, "
            "con rol PROPIETARIO, dentro de una única transacción."
        ),
    )
    def post(self, request, *args, **kwargs):

        # 1. Validar los datos recibidos.
        serializer = RegistrarPropietarioSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        # 2. Ejecutar el caso de uso.
        
        try:
            resultado = RegistrarPropietarioUseCase.execute(
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
        response_serializer = RegistrarPropietarioResponseSerializer(
            resultado
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )