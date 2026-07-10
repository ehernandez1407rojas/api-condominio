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
    path('api/casa_departamento/posteriores/<aaaa:anio>/', views.CasasDepartamentosPorFecha.as_view()),
    path('api/casa_departamento/titular', views.CasaDepartamentoPorTitular.as_view()),
    path('api/casa_departamento/filtrar', views.CasaDepartamentoPorTitularYCondominio.as_view()),
    path('api/casa_departamento/detalle/<pk>/', views.CasaDepartamentoDetalle.as_view()),
    path('api/saludo-postman', views.SaludoPostman.as_view()),
    path('api/cuota_cobrada/registrar/', views.CuotaCobradaGuardar.as_view()),
    ## path('api/casa-departamento/registrar/', views.CasaDepartamentoCreateAPIView.as_view()),
    path('api/condominio/registrar', views.CondominioCreateAPIView.as_view()),
    path('api/condominio/actualizar/<pk>', views.CondominioUpdateAPIView.as_view()),
    path('api/casa-departamento/registar', views.CasaDepartamentoCreateAPIView.as_view()),
    path('api/casa-departamento/actualizar/<pk>', views.CasaDepartamentoUpdateAPIView.as_view()),
    path('api/usuario/login/', views.LoginView.as_view(), name='login'),
    path('api/usuario/registrar/', views.RegistrarUsuarioView.as_view(), name='registrar'),
    
]

