from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password  # 👈 Importar
from django.utils import timezone
import hashlib

from ...models import (
    Usuario,    
    TipoToken,
    TokenUsuario,    
)

class EstablecerPasswordConTokenUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        token,
        nuevo_password,               
    ):

        # 1. Validar que el token exista y sea válido
        try:
            token_obj = TokenUsuario.objects.get(
                token_hash=hashlib.sha256(str(token).encode('utf-8')).hexdigest(),
                fecha_cancelacion__isnull=True,
                fecha_uso__isnull=True,
                fecha_expiracion__gt=timezone.now(),                
            )
            
            usuario = token_obj.usuario
            
        except TokenUsuario.DoesNotExist:
            raise ValidationError(
                'El token no es válido o ya no está disponible para su uso.'
            )

        # 2. Validar la nueva contraseña con Django (usando tu configuración de settings.py)
        try:
            validate_password(nuevo_password, usuario)
        except ValidationError as e:
            # Re-lanzar con el formato esperado
            raise ValidationError({
                'password': e.messages
            })

        # 3. Establecer nuevo password
        usuario.set_password(nuevo_password)
        usuario.save(update_fields=["password"]) 
        
        # 4. Marcar token como utilizado
        token_obj.fecha_uso = timezone.now()
        token_obj.save(update_fields=["fecha_uso"])

        # 5. Retornar respuesta
        return {
            "mensaje": "Contraseña establecida correctamente",
            "usuario": usuario.email_whatsapp,
        }