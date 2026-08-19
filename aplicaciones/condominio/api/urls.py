from django.urls import path, register_converter

from . import views
from . import converters

app_name = "condominio_app"

class DosDigitos:
    regex = '[0-9]+'
    
    def to_python(self, value):
        numero = int(value)
        if numero <100:
            return numero
        else:
            raise ValueError('error de número')
            
    def to_url(sel, value):
        return value
    
register_converter(DosDigitos, 'nn')    
register_converter(converters.ValidaAnios, 'aaaa')
    

urlpatterns = [
    path('api/condominio/lista', views.ListaCondominios.as_view()),
    path('api/condominio/filtro-nombre/<str:condominio>/', views.FiltroCondominio.as_view()),
    path('api/condominio/filtro-folio/<nn:folio>/', views.CondominioPorFolio.as_view()),

    path('api/propiedad/posteriores/<aaaa:anio>/', views.PropiedadesPorFecha.as_view()),
    path('api/propiedad/propietario', views.PropiedadPorPropietario.as_view()),
    path('api/propiedad/filtrar', views.PropiedadPorPropietarioYCondominio.as_view()),
    path('api/propiedad/detalle/<pk>/', views.PropiedadDetalle.as_view()),
    
    path('api/cuota_cobrada/registrar/', views.CuotaCobradaGuardar.as_view()),
    
    path('api/condominio/registrar', views.CondominioCreateAPIView.as_view()),
    path( 'api/condominio/registrar-administrador/', views.RegistrarCondominioView.as_view(), name='registrar-condominio-administrador'),
    path('api/condominio/actualizar/<pk>', views.CondominioUpdateAPIView.as_view()),

    path('api/propiedad/registar', views.PropiedadCreateAPIView.as_view()),
    path('api/propiedad/actualizar/<pk>', views.PropiedadUpdateAPIView.as_view()),
    path('api/propiedad/registrar-propietario/', views.RegistrarPropietarioView.as_view(), name='registrar-propietario-propiedad'),

    path('api/usuario/login/', views.LoginView.as_view(), name='login'),
    path( 'api/usuario/cambiar-password/', views.CambiarPasswordView.as_view(), name='cambiar-password'),
    path('api/usuario/registrar/', views.RegistrarUsuarioView.as_view(), name='registrar'),
    
    
]

