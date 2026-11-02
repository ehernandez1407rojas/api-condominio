from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from ...models import (    Usuario,    UsuarioRol,    Rol,    )
# 👇 Import ABSOLUTO desde la raíz del proyecto
from infraestructure.decorators import manejar_unique_violation

class RegistrarConserjeUseCase:

    @staticmethod
    @transaction.atomic
    @manejar_unique_violation
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,       
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

        # 3. Buscar al usuario conserje por email_whatsapp.
        usuario = Usuario.objects.filter(
            email_whatsapp=email_whatsapp
        ).first()

        # 3.1. Crear el usuario si no existe.
        if usuario is None:
            usuario = Usuario.objects.create_user(
                email_whatsapp=email_whatsapp,
                nombre_completo=nombre_completo,
                condominio=condominio,
                usuario_creo=administrador
            )

        # 3.2. Validar el condominio del usuario existente.
        else:
            if usuario.condominio is None:
                usuario.condominio = condominio
                usuario.usuario_modifico=administrador
                usuario.save(
                    update_fields=['condominio','usuario_modifico', 'fecha_modificacion']
                )

            elif usuario.condominio != condominio:
                raise ValidationError(
                    'El usuario ya está registrado en otro condominio.'
                )

        # 4. Obtener el rol CONSERJE.
        rol_conserje = Rol.objects.get(
            clave="CONSERJE"
        )

        # 4.1. Buscar si ya tiene el rol CONSERJE activo.
        usuario_rol = UsuarioRol.objects.filter(
            condominio=condominio,
            usuario=usuario,
            rol=rol_conserje,
            activo=True
        ).first()

        # 4.2. Crear la relación si no existe.
        if usuario_rol is None:
            usuario_rol = UsuarioRol.objects.create(
                condominio=condominio,
                usuario=usuario,
                rol=rol_conserje,
                usuario_creo=administrador,
            ) 
        else:
            raise ValidationError(
                    f'El conserje: {nombre_completo} ya existe en ese condominio'
            )


        return {            
            "usuario": usuario,
            "usuario_rol": usuario_rol,
        }