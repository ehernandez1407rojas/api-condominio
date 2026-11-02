from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from ..models import UsuarioRol, Usuario


def obtener_condominio_y_validar_administrador(usuario):
    """
    Obtiene el condominio del usuario y valida que tenga
    rol ADMINISTRADOR activo en dicho condominio.

    Retorna:
        Condominio: El condominio del usuario.
    """

    condominio = usuario.condominio
    
    if not condominio:
        raise ValidationError(
            'El usuario administrador no tiene un condominio asignado.'
        )

    es_administrador = UsuarioRol.objects.filter(
        usuario=usuario,
        condominio=condominio,
        rol__clave='ADMINISTRADOR',
        activo=True
    ).filter(
        Q(
            fecha_fin__isnull=True
        ) |
        Q(
            fecha_fin__gte=timezone.localdate()
        )
    ).exists()

    if not es_administrador:
        raise ValidationError(
            'El usuario no tiene permisos de administrador en este condominio.'
        )

    return condominio



def obtener_roles_y_condominio(usuario):
    """
    Obtiene los roles activos del usuario y el condominio en el que esta asignado.

    Retorna:
        condominio: El objeto Condominio del usuario.
        roles: Lista de strings, ej. ['ADMINISTRADOR', 'CONSERJE']
    """

    # Si no es una instancia de Usuario, asume que es la PK y la busca
    if not isinstance(usuario, Usuario):
        try:
            usuario = Usuario.objects.get(pk=usuario)
        except Usuario.DoesNotExist:
            raise ValidationError(
                f"El usuario: {usuario} no existe."
            )

    # 1. Obtener el condominio directamente del usuario
    condominio = usuario.condominio 
    
    if not condominio:
        raise ValidationError(
            'El usuario no tiene un condominio asignado.'
        )

    # 2. Filtrar los roles activos en la base de datos
    # Usamos .values_list('rol__clave', flat=True) para traer solo los nombres
    roles_usuario = list(UsuarioRol.objects.filter(
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=timezone.localdate()),
        usuario=usuario,
        condominio=condominio,
        activo=True
    ).values_list('rol__clave', flat=True)) 

    # 3. Validar si la lista está vacía
    if not roles_usuario:
        raise ValidationError(
            'El usuario no tiene un rol activo asignado en este condominio.'
        )
                
    return condominio, roles_usuario


