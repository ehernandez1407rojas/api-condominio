from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


from ...models import   GastoPagado
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class AutorizarGastoPagadoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,                
        gasto_pagado_id,        
                    
    ):        

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )       
                                
        # 2. Obtener el registro del Gasto Pagado  del condominio y bloquear la fila
        gasto_pagado = GastoPagado.objects.select_for_update().filter(
            pk=gasto_pagado_id,
            condominio=condominio
            ).first()
        
        if not gasto_pagado:
            raise ValidationError(
                'Este Gasto Pagado no existe en el condominio.'
            ) 

        # 3. Validar que el gasto pagado no este cancelado
        if gasto_pagado.esta_cancelado:
            raise ValidationError(
                'Este Gasto Pagado está cancelado y no puede ser autorizado.'
            )

        if gasto_pagado.esta_autorizado:
            raise ValidationError(
                'Este Gasto Pagado ya está autorizado.'
            )

        # 4 Autorizar el gasto pagado
        
        fecha_autorizacion = timezone.localdate() ## timezone.now().date() 

        gasto_pagado.esta_autorizado = True
        gasto_pagado.quien_autorizo = administrador
        gasto_pagado.cuando_autorizo = fecha_autorizacion
        gasto_pagado.usuario_modifico = administrador

        
        gasto_pagado.save(
            update_fields=[
                'esta_autorizado',
                'quien_autorizo',
                'cuando_autorizo',
                'usuario_modifico',
                'fecha_modificacion'
            ]
        )

        return {
            "descripcion": gasto_pagado.descripcion,
            "fecha": gasto_pagado.cuando_autorizo           
                    
        }