from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import date

from ...models import     CuotaCobrada, UsuarioRol


class ValidarCobroUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,                
        cuota_cobrada,
        comentario_validacion,
                    
    ):        

         # 1. Obtener el condominio del administrador.
        condominio = administrador.condominio

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )
        
        # 2. Validar que el usuario tenga rol ADMINISTRADOR activo.
        es_administrador = UsuarioRol.objects.filter(
            usuario=administrador,
            condominio=condominio,
            rol__clave='ADMINISTRADOR',
            activo=True
        ).filter(
            Q(fecha_fin__isnull=True) |
            Q(fecha_fin__gte=timezone.localdate())
        ).exists()

        if not es_administrador:
            raise ValidationError(
                'El usuario no tiene permisos de administrador en este condominio.'
        )
        
        # 3 Validar que el cobro es del condominio del administrador        

        if cuota_cobrada.condominio != condominio:
            raise ValidationError(
                'La cuota cobrada que se quiere validar no es del condominio.'
            )

        # 4.1 Obtener la cuota cobrada con bloqueo de fila.
        cuota_cobrada = CuotaCobrada.objects.select_for_update().get(
            pk=cuota_cobrada.pk
        )

        # 4 Validar que el cobro previamente no fue validado        
        
        if cuota_cobrada.esta_validada:
            raise ValidationError(
                'La cuota cobrada ya previamente fue validada'
            )
                        
        # 5. Actualizar la cuota cobrada con los datos del administrador            

        cuota_cobrada.quien_valido=administrador
        cuota_cobrada.cuando_valido=timezone.now()
        cuota_cobrada.esta_validada=True
        cuota_cobrada.comentario_validacion=comentario_validacion

        cuota_cobrada.save(update_fields=['quien_valido', 'cuando_valido', 'esta_validada', 'comentario_validacion'])


        return {
            "comentario": cuota_cobrada.comentario_validacion            
                    
        }