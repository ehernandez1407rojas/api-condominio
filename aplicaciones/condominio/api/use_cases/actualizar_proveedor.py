from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import Proveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarProveedorUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        proveedor_id,
        **campos_a_actualizar
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )
        
        # 2. Validar que haya enviado al menos un campo a actualizar
        if not campos_a_actualizar:            
            raise ValidationError(
                'Debe indicar al menos un campo para actualizar.'
            )

        # 3. Obtener el Proveedor del condominio y bloquear la fila
        proveedor = Proveedor.objects.select_for_update().filter(
            pk=proveedor_id,
            condominio=condominio
        ).first()

        if not proveedor:
            raise ValidationError(
                'Este proveedor no existe en el condominio.'
            )

        # 4. Validar celular que no se repita en otro proveedor  si se desea modificar
        celular = campos_a_actualizar.get('celular')
        
        if celular is not None:
            existe_proveedor = Proveedor.objects.filter(
                condominio=condominio,
                celular=celular
            ).exclude(
                pk=proveedor.pk
            ).exists()

            if existe_proveedor:
                raise ValidationError(
                    'Ya existe otro proveedor con ese celular '
                    'en el condominio.'
                )
            
        # 5. Validar correo que no se repita en otro proveedor  si se desea modificar
        correo = campos_a_actualizar.get('correo')

        if correo is not None:
            existe_proveedor = Proveedor.objects.filter(
                condominio=condominio,
                correo=correo
            ).exclude(
                pk=proveedor.pk
            ).exists()

            if existe_proveedor:
                raise ValidationError(
                    'Ya existe otro proveedor con ese correo '
                    'en el condominio.'
                )

        # 6. Actualizar únicamente los campos enviados y la auditoria        

        for clave, valor in campos_a_actualizar.items():            
            setattr(proveedor, clave, valor)

        proveedor.usuario_modifico = administrador

        # 7. Guardar cambios
        campos_a_guardar = list(campos_a_actualizar.keys())+['usuario_modifico', 'fecha_modificacion']
        proveedor.save(
            update_fields=campos_a_guardar
        )

        # 8. Respuesta
        return {
            "id": proveedor.id,
            "nombre": proveedor.nombre,
            "direccion": proveedor.direccion,
            "celular": proveedor.celular,  
        }