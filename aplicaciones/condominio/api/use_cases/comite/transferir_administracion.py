from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ....models import (
    Comite,
    ComiteIntegrante,
    Rol,
    TransferenciaAdministracion,
    UsuarioRol,
)
from ....utilidades.validaciones import (
    obtener_condominio_y_validar_administrador,
)


class TransferirAdministracionUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador_actual,
        administrador_nuevo,
        comentario,
    ):

        # 1. Obtener el condominio y validar que el usuario
        #    actual sea el administrador.
        condominio = obtener_condominio_y_validar_administrador(
            administrador_actual
        )

        # 2. El nuevo administrador debe ser diferente
        #    al administrador actual.
        if administrador_actual == administrador_nuevo:
            raise ValidationError(
                "El nuevo administrador debe ser diferente "
                "al administrador actual."
            )

        # 3. Obtener el rol PROPIETARIO.
        rol_propietario = Rol.objects.get(
            clave="PROPIETARIO"
        )

        # 4. Validar que el nuevo administrador sea
        #    propietario activo del condominio.
        propietario_activo = UsuarioRol.objects.filter(
            condominio=condominio,
            usuario=administrador_nuevo,
            rol=rol_propietario,
            activo=True,
        ).exists()

        if not propietario_activo:
            raise ValidationError(
                "El nuevo administrador debe ser un propietario "
                "activo del condominio."
            )

        # 5. Obtener y bloquear el comité activo.
        try:
            comite = Comite.objects.select_for_update().get(
                condominio=condominio,
                activo=True,
            )
        except Comite.DoesNotExist:
            raise ValidationError(
                "No es posible transferir la administración porque "
                "el condominio no tiene un comité activo. "
                "Registre un comité antes de realizar la transferencia."
            )

        fecha_actual = timezone.localdate()

        # 6. Obtener el rol ADMINISTRADOR.
        rol_administrador = Rol.objects.get(
            clave="ADMINISTRADOR"
        )

        # 7. Inactivar el rol ADMINISTRADOR anterior.
        UsuarioRol.objects.filter(
            condominio=condominio,
            usuario=administrador_actual,
            rol=rol_administrador,
            activo=True,
        ).update(
            activo=False,
            fecha_fin=fecha_actual,
            usuario_modifico=administrador_actual,
            fecha_modificacion=timezone.now(),
        )

        # 8. Crear el nuevo rol como ADMINISTRADOR.
        UsuarioRol.objects.create(
            condominio=condominio,
            usuario=administrador_nuevo,
            rol=rol_administrador,
            fecha_fin=None,
            activo=True,
            usuario_creo=administrador_actual,
        )

        # 9. Inactivar los integrantes activos del comité.
        ComiteIntegrante.objects.filter(
            comite=comite,
            activo=True,
        ).update(
            activo=False,
            aplica_hasta=fecha_actual,
            usuario_modifico=administrador_actual,
            fecha_modificacion=timezone.now(),
        )

        # 10. Inactivar el comité.
        Comite.objects.filter(
            pk=comite.pk
        ).update(
            activo=False,
            aplica_hasta=fecha_actual,
            usuario_modifico=administrador_actual,
            fecha_modificacion=timezone.now(),
        )

        # 11. Registrar la transferencia de la administracion del condominio
        transferencia = TransferenciaAdministracion.objects.create(
            condominio=condominio,
            administrador_anterior=administrador_actual,
            administrador_nuevo=administrador_nuevo,
            comite_inactivado=comite,
            fecha_transferencia=fecha_actual,
            comentario=comentario,
            usuario_creo=administrador_actual,
        )

        # 12. Regresar información de la transferencia.
        return {
            "id": transferencia.id,
            "administrador_anterior": (
                administrador_actual.nombre_completo
            ),
            "administrador_nuevo": (
                administrador_nuevo.nombre_completo
            ),
            "fecha_transferencia": fecha_actual,
        }