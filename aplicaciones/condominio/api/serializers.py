from rest_framework import serializers, pagination
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.utils import timezone
from django.db.models import Q
from .constants import PASSWORD_MIN_LENGTH, MESES_EXIGIBLES_POSTERIORES_HOY

from ..models import *


class PaginationSerializer(pagination.PageNumberPagination):
    page_size = 3
    max_page_size = 20


class CreoModificoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion', 'usuario_modifico')
                
    """ def create(self, validated_data):
        validated_data['usuario_creo'] = self.context['request'].user
        return super().create(validated_data) """
    
    def to_internal_value(self, data):
        # Convierte campos específicos a mayúsculas antes de validar
        uppercase_fields = self.get_string_fields()  # Método que puedes sobrescribir en hijos
        for field in uppercase_fields:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].upper()
                
         # Opcional: Validar formato de correo (si es sensible a mayúsculas)
        if 'correo' in data:
            data['correo'] = data['correo'].lower()  # Ejemplo: correo siempre en minúsculas
            
        return super().to_internal_value(data)
    
    def get_string_fields(self):
        """Obtiene automáticamente todos los campos CharField del modelo"""
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'model'):
            return []
            
        from django.db.models import CharField, TextField
        string_fields = []
        
        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, (CharField, TextField)):
                string_fields.append(field.name)
        
        return string_fields
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega claims personalizados
        token['user_id'] = user.id
        token['condominio_id'] = user.condominio.id if user.condominio else None
        # token['tipo_usuario'] = user.tipo_usuario
        token['nombre_completo'] = user.nombre_completo

        if user.condominio:
            roles = UsuarioRol.objects.filter(
                usuario=user,
                condominio=user.condominio,
                activo=True
            ).filter(
                Q(fecha_fin__isnull=True) |
                Q(fecha_fin__gte=timezone.localdate())
            ).values_list(
                'rol__clave',
                flat=True
            )

            token['roles'] = list(roles)
        else:
            token['roles'] = []

        return token
    
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
            
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'email_whatsapp', 
            'nombre_completo',                                     
            'password'            
        ]
        extra_kwargs = {
            'password': {'write_only': True}                        
        }

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            email_whatsapp=validated_data['email_whatsapp'],
            nombre_completo=validated_data['nombre_completo'],
            password=validated_data['password'],                        
        )
        return user

# seralizaser de las tablas transaccionales ---        
class CondominioSerializer(CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):        
        model = Condominio
        fields = ['id', 'nombre', 'direccion']        
                
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo

# 1. Serializer para la PETICIÓN (Request)
class RegistrarCondominioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    nombre_corto = serializers.CharField(max_length=20)
    direccion = serializers.CharField(max_length=100)
    inicio_servicio = serializers.DateField()

    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )

# 2. (Opcional) Serializer para la RESPUESTA (Response)
class RegistrarCondominioResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField(        source="condominio.id"    )
    nombre = serializers.CharField(        source="condominio.nombre"    )
    nombre_corto = serializers.CharField(        source="condominio.nombre_corto"    )
    usuario_id = serializers.IntegerField(        source="usuario.id"    )
    nombre_completo = serializers.CharField(        source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField(        source="usuario.email_whatsapp"    )    
    rol = serializers.CharField(        source="usuario_rol.rol.clave"    ) 

class UsuarioRolSerializer(serializers.Serializer):
    class Meta:
        model = UsuarioRol
        fields = (
            '__all__'
    )

class PropiedadSerializer(CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):
        model = Propiedad
        
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo
    
                        


class EstadoCondominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCondominio
        fields = (
            '__all__'
        )        

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = (
            '__all__'
        )         

class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(
        write_only=True
    )

    password_nueva = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )        

class CambiarPasswordResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()    

# # Serializer de entrada para registrar un propietario y su propiedad.
class RegistrarPropietarioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)    
    direccion = serializers.CharField(max_length=100)    

    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

#  (Opcional) Serializer para la RESPUESTA del resgistro propiedad
class RegistrarPropietarioResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField( source="propiedad.condominio.id"    )
    nombre = serializers.CharField( source="propiedad.nombre"    )    
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )       

class TokenUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenUsuario
        fields = (
            '__all__'
    )    

class TipoTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoToken
        fields = (
            '__all__'
    )         

class GenerarTokenSerializer(serializers.Serializer):
    email_whatsapp = serializers.CharField(max_length=50)
    tipo_token = serializers.CharField(max_length=50)

class GenerarTokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
                    
class EstablecerPasswordSerializer(serializers.Serializer):
    token = serializers.IntegerField()
    nuevo_password = serializers.CharField(
        write_only=True,
        max_length=50,
        min_length=PASSWORD_MIN_LENGTH)

class EstablecerPasswordResponseSerializer(serializers.Serializer):    
    mensaje = serializers.CharField(max_length=50)    
                  

# # Serializer de entrada para registrar un propietario y su propiedad.
class RegistrarPropietarioTokenSerializer(serializers.Serializer):
    nombre_propiedad = serializers.CharField(max_length=50)    
    direccion = serializers.CharField(max_length=100)    

    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

#  Serializer para la RESPUESTA del resgistro propiedad, propietario y token
class RegistrarPropietarioTokenResponseSerializer(serializers.Serializer):
    condominio_id = serializers.IntegerField( source="propiedad.condominio.id"    )
    nombre = serializers.CharField( source="propiedad.nombre"    )    
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )    
    token_temporal = serializers.IntegerField() 

# # Serializer de entrada para registrar un conserje.
class RegistrarConserjeTokenSerializer(serializers.Serializer):    
    email_whatsapp = serializers.CharField(max_length=50)
    nombre_completo = serializers.CharField(max_length=150)

# # Serializer de respuesta para registrar un conserje.
class RegistrarConserjeTokenResponseSerializer(serializers.Serializer): 
    condominio_id = serializers.IntegerField( source="usuario.condominio.id"    )   
    usuario_id = serializers.IntegerField( source="usuario.id"    )
    nombre_completo = serializers.CharField( source="usuario.nombre_completo"    )
    email_whatsapp = serializers.CharField( source="usuario.email_whatsapp"    )
    rol = serializers.CharField( source="usuario_rol.rol.clave"    )    
    token_temporal = serializers.IntegerField() 


# la basica que pone todos los campos en el payload
# se descarta en requerimientos reales de negocio
""" 
class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ('__all__')

class CuotaCobradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaCobrada
        fields = (
            '__all__'
    )     
"""

# # Serializer  para registrar una cuota y las cuotas exigibles de manera interna a los propietarios
class DefinirCuotaSerializer(serializers.Serializer): 
    tipo_cuota = serializers.PrimaryKeyRelatedField(
        queryset=TipoCuota.objects.all()
        )   
    nombre = serializers.CharField(max_length=100)
    importe = serializers.DecimalField(decimal_places=2, max_digits=12)
    aplica_desde = serializers.DateField()
    aplica_hasta = serializers.DateField()    
    
# # Serializer de respuesta por el registro una cuota y las cuotas exigibles de manera interna a los propietarios
class DefinirCuotaResponseSerializer(serializers.Serializer): 
    nombre = serializers.CharField()
    tipo_cuota = serializers.CharField()
    cuotas_exigibles = serializers.IntegerField()

  
# # Serializer  para registrar la cancelacion de una cuota y las cuotas exigibles pendientes de manera interna a los propietarios
class CancelarCuotaSerializer(serializers.Serializer): 
    cuota = serializers.PrimaryKeyRelatedField(
            queryset=Cuota.objects.all()
        )    
    comentario_cancelacion = serializers.CharField(max_length=100)

# # Serializer  para la respuesta de registrar la cancelacion de una cuota y las cuotas exigibles pendientes de manera interna a los propietarios
class CancelarCuotaResponseSerializer(serializers.Serializer): 
    nombre = serializers.CharField()   
    tipo_cuota = serializers.CharField()
    cuotas_exigibles_canceladas = serializers.IntegerField()    

# # Serializer  para registrar el cobro de una cuota
class CobrarCuotaSerializer(serializers.Serializer): 
    propiedad = serializers.PrimaryKeyRelatedField(queryset=Propiedad.objects.all())
    cuota_exigible = serializers.PrimaryKeyRelatedField(queryset=CuotaExigible.objects.all())
    importe_cobrado = serializers.DecimalField(decimal_places=2, max_digits=12)
    descripcion_comprobante = serializers.CharField(max_length=100)


# # Serializer  para la respuesta de registrar el cobro de una cuota
class CobrarCuotaResponseSerializer(serializers.Serializer): 
    propiedad = serializers.CharField()   
    importe_cobrado = serializers.DecimalField(decimal_places=2, max_digits=12)


# # Serializer  para validar el cobro de una cuota
class ValidarCobroSerializer(serializers.Serializer):     
    cuota_cobrada = serializers.PrimaryKeyRelatedField(queryset=CuotaCobrada.objects.all())    
    comentario_validacion = serializers.CharField(max_length=100)


# # Serializer  para la respuesta de validar el cobro de una cuota
class ValidarCobroResponseSerializer(serializers.Serializer): 
    comentario = serializers.CharField()   
    

     