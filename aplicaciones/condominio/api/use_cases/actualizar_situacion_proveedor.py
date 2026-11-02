from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import Proveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarSituacionProveedorUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        proveedor_id,
        situacion_proveedor
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )               

        # 2. Obtener el Proveedor del condominio y bloquear la fila
        proveedor = Proveedor.objects.select_for_update().filter(
            pk=proveedor_id,
            condominio=condominio
        ).first()

        if not proveedor:
            raise ValidationError(
                'Este proveedor no existe en el condominio.'
            )        

        # 3. Actualizar la situacion del proveedor y los campos de auditoria                
        proveedor.usuario_modifico = administrador
        proveedor.situacion = situacion_proveedor
        
        proveedor.save(update_fields=[ 'situacion', 'usuario_modifico', 'fecha_modificacion'])
        

        # 5. Respuesta
        return {            
            "nombre": proveedor.nombre,
            "situacion": proveedor.situacion.clave,             
        }