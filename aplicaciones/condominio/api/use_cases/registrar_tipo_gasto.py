from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import TipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador
# 👇 Import ABSOLUTO desde la raíz del proyecto
from infraestructure.decorators import manejar_unique_violation


class RegistrarTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    @manejar_unique_violation
    def execute(
        *,
        administrador,        
        clave,
        descripcion,
        orden             
    ):        

        # 1. Obtener el condominio del usuario y que tenga rol de administrador mediante la funcion
        condominio = obtener_condominio_y_validar_administrador(administrador)
        
                
        # 2. Validar que la clave no se repita en ese condominio        

        existe_tipo_gasto  = TipoGasto.objects.filter(
            condominio=condominio,
            clave=clave            
        ).exists()

        if existe_tipo_gasto:
            raise ValidationError(
                f'Ya existe un tipo gasto con esa clave en ese condominio.'
            )        

        # 3 Crear el Tipo Gasto
        tipo_gasto = TipoGasto.objects.create(
            condominio=condominio,            
            clave=clave,
            descripcion=descripcion,
            orden=orden, 
            usuario_creo=administrador,

        )
        
        
        return {
            "id": tipo_gasto.id,
            "clave": tipo_gasto.clave,
            "descripcion": tipo_gasto.descripcion,
            "orden": tipo_gasto.orden,                   
        }