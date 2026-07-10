from rest_framework import serializers, pagination
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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
    
    """ def get_uppercase_fields(self):
        # Lista base de campos a convertir (puede extenderse en clases hijas)
        return ['nombre', 'direccion', 'titular']  # Campos comunes en tus modelos """

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agrega claims personalizados
        token['user_id'] = user.id
        token['condominio_id'] = user.condominio.id if user.condominio else None
        token['tipo_usuario'] = user.tipo_usuario
        token['nombre_completo'] = user.nombre_completo

        return token
    
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    condominio_id = serializers.PrimaryKeyRelatedField(
        queryset=Condominio.objects.all(), 
        source='condominio',
        write_only=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 
            'email_whatsapp', 
            'nombre_completo', 
            'tipo_usuario',
            'condominio_id',
            'casa_departamento',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'tipo_usuario': {'required': True}
        }

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            email_whatsapp=validated_data['email_whatsapp'],
            nombre_completo=validated_data['nombre_completo'],
            password=validated_data['password'],
            tipo_usuario=validated_data.get('tipo_usuario', 'PROPIETARIO'),
            condominio=validated_data.get('condominio')
        )
        return user

# seralizaser de las tablas transaccionales ---        
class CondominioSerializer(CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):        
        model = Condominio
        
        
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo

class CasaDepartamentoSerializer(CreoModificoSerializer):
    class Meta(CreoModificoSerializer.Meta):
        model = CasaDepartamento
        
    def get_string_fields(self):
        base_fields = super().get_string_fields()
        return [field for field in base_fields if field != 'correo']  # Excluye campo
    
                        
class CuotaCobradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaCobrada
        fields = (
            '__all__'
        )