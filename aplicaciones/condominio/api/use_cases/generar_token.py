from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import hashlib

from datetime import timedelta
import secrets

from ...models import (
    Usuario,    
    TipoToken,
    TokenUsuario,    
)

class GenerarTokenUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        tipo_token,        
    ):

        # 1. Obtener el condominio del administrador.
        condominio = administrador.condominio

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )
        
        # 2. verifica que el usuario exista con ese correo/whatsapp.
        usuario = Usuario.objects.filter(
            email_whatsapp=email_whatsapp
        ).first()

        # 3. Crear el token temporal.
        #    Si existe un token vigente del mismo tipo, se cancela antes de generar el nuevo.
        
        if usuario :

            tipo_token_obj = TipoToken.objects.get(
                    clave=tipo_token
                )
            fecha_hora_actual=timezone.now()

            token_vigente = TokenUsuario.objects.filter(
                    usuario=usuario,
                    tipo=tipo_token_obj,
                    fecha_uso__isnull=True,
                    fecha_cancelacion__isnull=True,
                    fecha_expiracion__gt=fecha_hora_actual,
                ).first()

            if token_vigente :
                token_vigente.fecha_cancelacion = fecha_hora_actual
                token_vigente.save(update_fields=["fecha_cancelacion"])

            token_temporal = secrets.randbelow(900000) + 100000
            token_hash = hashlib.sha256(str(token_temporal).encode('utf-8')).hexdigest()                        

            token_usuario = TokenUsuario.objects.create(
                condominio=condominio,
                usuario=usuario,
                token_hash=token_hash,
                tipo=tipo_token_obj,
                fecha_generacion= fecha_hora_actual,
                fecha_expiracion = (
                        fecha_hora_actual
                                + timedelta(minutes=tipo_token_obj.duracion_minutos) ),                            
                usuario_creo=administrador,
            )
            
        # 3.1. El usuario no existe.
        else:
            raise ValidationError(
                'El usuario no existe.'
            )

        # 4 regresa el usuario token temporal
        return {
             "token": token_temporal           
        }