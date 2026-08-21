# nuevo archivo: registrar_propietario_con_token.py
from django.db import transaction
from django.core.exceptions import ValidationError

from .registrar_propietario import RegistrarPropietarioUseCase
from .generar_token import GenerarTokenUseCase


class RegistrarPropietarioConTokenUseCase:
    """Orquesta el registro de propietario y generación de token"""
    
    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,
        nombre_propiedad,
        direccion,
    ):
        # 1. Registrar al propietario
        resultado_registro = RegistrarPropietarioUseCase.execute(
            administrador=administrador,
            email_whatsapp=email_whatsapp,
            nombre_completo=nombre_completo,
            nombre=nombre_propiedad,
            direccion=direccion,
        )
        
        # 2. Generar token para establecer contraseña
        try:
            resultado_token = GenerarTokenUseCase.execute(
                administrador=administrador,
                email_whatsapp=email_whatsapp,
                tipo_token='REGISTRO_PROPIETARIO',
            )
        except ValidationError as e:
            # Si falla la generación del token, la transacción hace rollback
            raise ValidationError(
                f"Error al generar token: {e.messages}"
            )
        
        # 3. Combinar resultados
        
        return {
            **resultado_registro,
            "token_temporal": resultado_token["token"],
            "mensaje": "Propietario registrado. Token generado para establecer contraseña."
        }