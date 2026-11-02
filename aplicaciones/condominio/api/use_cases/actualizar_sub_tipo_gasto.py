from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import SubTipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarSubTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        sub_tipo_gasto_id,            
        clave=None,
        descripcion=None,
        orden=None
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        # 2. Validar que se haya enviado al menos un campo
        # Genero un diccionario
        campos = {
            'clave': clave,
            'descripcion': descripcion,
            'orden': orden,
        }


        if not any(valor is not None for valor in campos.values()):            
            raise ValidationError(
                'Debe indicar al menos un campo para actualizar.'
            )

        # 3. Obtener el SubTipoGasto del condominio y bloquear la fila
        sub_tipo_gasto = SubTipoGasto.objects.select_for_update().filter(
            pk=sub_tipo_gasto_id,
            condominio=condominio
        ).first()

        if not sub_tipo_gasto:
            raise ValidationError(
                'Ese sub tipo de gasto no existe en el condominio.'
            )

        # 4. Validar clave en caso de que se desea modificar
        if clave is not None:
            existe_sub_tipo_gasto = SubTipoGasto.objects.filter(
                condominio=condominio,
                tipo_gasto=sub_tipo_gasto.tipo_gasto,
                clave=clave
            ).exclude(
                pk=sub_tipo_gasto.pk
            ).exists()

            if existe_sub_tipo_gasto:
                raise ValidationError(
                    'Ya existe un sub tipo de gasto con esa clave '
                    'en el condominio.'
                )

        # 5. Actualizar únicamente los campos enviados y la auditoria
        if clave is not None:
            sub_tipo_gasto.clave = clave

        if descripcion is not None:
            sub_tipo_gasto.descripcion = descripcion

        if orden is not None:
            sub_tipo_gasto.orden = orden

        sub_tipo_gasto.usuario_modifico = administrador

        # 6. Guardar cambios
        sub_tipo_gasto.save(
            update_fields=['clave', 'descripcion', 'orden', 'usuario_modifico', 'fecha_modificacion']
        )

        # 6. Respuesta
        return {
            "id": sub_tipo_gasto.id,
            "clave": sub_tipo_gasto.clave,
            "descripcion": sub_tipo_gasto.descripcion,
            "orden": sub_tipo_gasto.orden,
        }