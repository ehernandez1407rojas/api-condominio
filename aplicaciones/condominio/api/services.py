# services.py
from django.db import transaction
from ..models import Usuario, Condominio
from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer, CondominioSerializer, UsuarioRolSerializer

class RegistroCondominioService:

    @staticmethod
    @transaction.atomic
    def registrar_usuario_y_condominio(user_data: dict, condominio_data: dict) -> dict:
        # 1. Crear usuario
        # Asumiendo que usas un serializer para validar previamente en la vista
        usuario_serializer = UsuarioSerializer(data=user_data)
        usuario_serializer.is_valid(raise_exception=True)
        usuario = usuario_serializer.save()    
        
        # 3. Crear condominio
        condominio_serializer = CondominioSerializer(data=condominio_data)
        condominio_serializer.is_valid(raise_exception=True)
        condominio = condominio_serializer.save()

        # 3.1 crea el roll de administrador al usuario
        usuario_rol_serializer = UsuarioRolSerializer

        # 4. Generar tokens de acceso
        token_serializer = CustomTokenObtainPairSerializer(data={
            'email_whatsapp': usuario.email_whatsapp,
            'password': user_data.get('password')
        })
        token_serializer.is_valid(raise_exception=True)

        return {
            'user': usuario_serializer.data,
            'condominio': condominio_serializer.data,
            'access': token_serializer.validated_data['access'],
            'refresh': token_serializer.validated_data['refresh']
        }