from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError  # 👈 Aliás para DRF # 👈 DRF ValidationError
from django.contrib.auth.password_validation import validate_password

from ...models import Condominio, Usuario, UsuarioRol, Rol


class RegistrarCondominioUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        nombre,
        nombre_corto,
        direccion,
        inicio_servicio,
        email_whatsapp,
        nombre_completo,
        password,
    ):
        # 0.1 Crear un usuario temporal para aplicar las validaciones del password que se heredan de USER
        usuario_temporal = Usuario(
            email_whatsapp=email_whatsapp,
            nombre_completo=nombre_completo,
        )
        
        try:
            validate_password(password, usuario_temporal)
        except ValidationError as e:  # ✅ Usa ValidationError directamente (no django.core.exceptions.ValidationError)
            # DRF ValidationError maneja esto correctamente
            raise DRFValidationError({
                'password': e.messages
            })

        # 
        #  1. Crear el condominio.
        # NOTA: El administrador todavía no existe.
        condominio = Condominio.objects.create(
            nombre=nombre,
            nombre_corto=nombre_corto,
            direccion=direccion,
            inicio_servicio=inicio_servicio,
        )

        # 2. Crear el usuario administrador.
       
        usuario = Usuario.objects.create_user(
            email_whatsapp=email_whatsapp,
            nombre_completo=nombre_completo,
            password=password,
            condominio=condominio,
        )

        # 3. Completar la auditoría del condominio.
        condominio.usuario_creo = usuario
        condominio.save(update_fields=["usuario_creo"])

        # 4. Obtener el rol ADMINISTRADOR.
        rol_administrador = Rol.objects.get(
            clave="ADMINISTRADOR"
        )

        # 5. Crear la relación usuario-condominio-rol.
        usuario_rol = UsuarioRol.objects.create(
            condominio=condominio,
            usuario=usuario,
            rol=rol_administrador,
            usuario_creo=usuario,
        )

        return {
            "condominio": condominio,
            "usuario": usuario,
            "usuario_rol": usuario_rol,
        }