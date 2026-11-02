from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ...utilidades.validaciones import obtener_condominio_y_validar_administrador
from ...models import   GastoPagado


class CancelarGastoPagadoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,        
        gasto_pagado_id,
        motivo_cancelacion
                     
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
                            'Este Gasto Pagado no se puede volver a cancelar.'
                        ) 

                         
        # 4 Cancelar el gasto pagado

        fecha_cancelacion = timezone.localdate() ## timezone.now().date() 

        gasto_pagado.esta_cancelado = True
        gasto_pagado.quien_cancelo = administrador
        gasto_pagado.cuando_cancelo = fecha_cancelacion
        gasto_pagado.motivo_cancelacion = motivo_cancelacion
        gasto_pagado.usuario_modifico=administrador
        gasto_pagado.save(
            update_fields=[
                'esta_cancelado',
                'quien_cancelo',
                'cuando_cancelo',
                'motivo_cancelacion',
                'usuario_modifico',
                'fecha_modificacion'
            ]
        )
                
       
        # 5. Datos de respuesta

        return {
            "gasto": gasto_pagado.descripcion,
            "motivo_cancelacion": gasto_pagado.motivo_cancelacion,
            "fecha": gasto_pagado.cuando_cancelo 
           
        }