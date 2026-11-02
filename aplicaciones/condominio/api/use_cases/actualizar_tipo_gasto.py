from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import TipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        tipo_gasto_id,
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

        # 3. Obtener el TipoGasto del condominio y bloquear la fila
        tipo_gasto = TipoGasto.objects.select_for_update().filter(
            pk=tipo_gasto_id,
            condominio=condominio
        ).first()

        if not tipo_gasto:
            raise ValidationError(
                'Ese tipo de gasto no existe en el condominio.'
            )

        # 4. Validar clave si se desea modificar
        if clave is not None:
            existe_tipo_gasto = TipoGasto.objects.filter(
                condominio=condominio,
                clave=clave
            ).exclude(
                pk=tipo_gasto.pk
            ).exists()

            if existe_tipo_gasto:
                raise ValidationError(
                    'Ya existe un tipo de gasto con esa clave '
                    'en el condominio.'
                )

        # 5. Actualizar únicamente los campos enviados y la auditoria
        if clave is not None:
            tipo_gasto.clave = clave

        if descripcion is not None:
            tipo_gasto.descripcion = descripcion

        if orden is not None:
            tipo_gasto.orden = orden

        tipo_gasto.usuario_modifico = administrador

        # 6. Guardar cambios
        tipo_gasto.save(
            update_fields=['clave', 'descripcion', 'orden', 'usuario_modifico', 'fecha_modificacion']
        )

        # 6. Respuesta
        return {
            "id": tipo_gasto.id,
            "clave": tipo_gasto.clave,
            "descripcion": tipo_gasto.descripcion,
            "orden": tipo_gasto.orden,
        }