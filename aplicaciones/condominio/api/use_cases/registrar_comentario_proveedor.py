from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import ProveedorComentario , Proveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class RegistrarComentarioProveedorUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
            *,
        administrador,
        proveedor,
        comentario
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )              
                
        # 2. Verificar que el proveedor exista
        proveedor = Proveedor.objects.filter(
            pk=proveedor.id,
            condominio=condominio
        ).first()

        if not proveedor:
            raise ValidationError(
                'Este proveedor no existe en el condominio.'
            )        
            
        
        # 5 Insertar el comentario al  Proveedor
        comentario_obj = ProveedorComentario.objects.create(
            condominio=condominio,
            proveedor = proveedor,
            comentario = comentario,
            usuario_creo = administrador
        )
                
        return {            
            "nombre": proveedor.nombre,
            "comentario": comentario_obj.comentario                              
        }