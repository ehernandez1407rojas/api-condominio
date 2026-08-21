# nuevo archivo: registrar_propietario_con_token.py
from django.db import transaction
from django.core.exceptions import ValidationError

from .registrar_conserje import RegistrarConserjeUseCase
from .generar_token import GenerarTokenUseCase


class RegistrarConserjeConTokenUseCase:
    """Orquesta el registro del conserje y generación de token"""
    
    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,
        
    ):
        # 1. Registrar al conserje
        try:
            resultado_registro = RegistrarConserjeUseCase.execute(
                        administrador=administrador,
                        email_whatsapp=email_whatsapp,
                        nombre_completo=nombre_completo,
                        
                    )
        except ValidationError as e:
            # si falla la creacion del conserje, se sale de la transaccion
            raise ValidationError(
                f"Error al crear conserje: {e.messages}"
            )            
        
                
        # 2. Generar token para establecer contraseña
        try:
            resultado_token = GenerarTokenUseCase.execute(
                administrador=administrador,
                email_whatsapp=email_whatsapp,
                tipo_token='REGISTRO_CONSERJE',
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
            "mensaje": "Conserje registrado. Token generado para establecer contraseña."
        }