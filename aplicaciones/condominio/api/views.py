from django.shortcuts import render
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import *
from .serializers import *

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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
    
class CasasDepartamentosPorFecha(ListAPIView):
    serializer_class = CasaDepartamentoSerializer
    pagination_class = PaginationSerializer
    
    def get_queryset(self):
        anio = self.kwargs['anio']
        queryset = CasaDepartamento.objects.lista_casas_departamentos_posteriores(anio)
        return queryset
    
class CasaDepartamentoPorTitular(ListAPIView):
    serializer_class = CasaDepartamentoSerializer
    
    def get_queryset(self):
        titular = self.request.query_params.get('titular', '')
        queryset = CasaDepartamento.objects.casas_departamentos_por_titular(titular)        
        return queryset
    
class CasaDepartamentoPorTitularYCondominio(ListAPIView):
    serializer_class = CasaDepartamentoSerializer
    pagination_class = PaginationSerializer
    
    def get_queryset(self):
        titular = self.request.query_params.get('titular', '')
        condominio = self.request.query_params.get('condominio', 1)
        queryset = CasaDepartamento.objects.casas_departamentos_por_titular_y_condominio(titular, condominio)        
        return queryset
    
class CasaDepartamentoDetalle(RetrieveAPIView):
    serializer_class = CasaDepartamentoSerializer
     ## queryset = CasaDepartamento.objects.all()
     
    def retrieve(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializers = self.get_serializer(instancia)
        return Response(serializers.data)
     
    def get_queryset(self):
        queryset = CasaDepartamento.objects.filter(            
            condominio__icontains = "Cabacano" 
        )        
        return queryset
        
    
class SaludoPostman(APIView):
    
    def get(self, request):
        return Response({"estado": "ok el GET"})
    
    def post(self, request):
        return Response({"estado": "ok el POST"})
    
    def delete(self, request):
        return Response({"estado": "ok el DELETEee"})
        
class CuotaCobradaGuardar(CreateAPIView):
    serializer_class = CuotaCobradaSerializer
    queryset = CuotaCobrada.objects.all()
    
class CasaDepartamentoCreateAPIView(CreateAPIView):
    serializer_class = CasaDepartamentoSerializer
    queryset = CasaDepartamento.objects.all()
    
class CasaDepartamentoUpdateAPIView(UpdateAPIView):
    serializer_class = CasaDepartamentoSerializer
    queryset = CasaDepartamento.objects.all()

    
@extend_schema(
    request=CondominioSerializer,
    responses=CondominioSerializer,
)    
class CondominioCreateAPIView(CreateAPIView):
    serializer_class = CondominioSerializer
    queryset = Condominio.objects.all()
    
class CondominioUpdateAPIView(UpdateAPIView):
    serializer_class = CondominioSerializer
    queryset = CasaDepartamento.objects.all()