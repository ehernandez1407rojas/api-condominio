from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import  SubTipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador
# 👇 Import ABSOLUTO desde la raíz del proyecto
from infraestructure.decorators import manejar_unique_violation


class RegistrarSubTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    @manejar_unique_violation
    def execute(
        *,
        administrador,
        tipo_gasto,        
        clave,
        descripcion,
        orden             
    ):        

        # 1. Obtener el condominio del usuario y que tenga rol de administrador mediante la funcion
        condominio = obtener_condominio_y_validar_administrador(administrador)

        # 1.1 Validar que el tipo de gasto sea del condominio
        if tipo_gasto.condominio_id != condominio.id:
            raise ValidationError(
                'El tipo de gasto no pertenece al condominio del administrador.'
            )
                
        # 2. Validar que la clave no se repita en ese condominio en ese  tipo gasto       

        existe_sub_tipo_gasto  = SubTipoGasto.objects.filter(
            condominio=condominio,
            tipo_gasto=tipo_gasto,
            clave=clave            
        ).exists()

        if existe_sub_tipo_gasto:
            raise ValidationError(
                f'Ya existe un subtipo gasto con esa clave en ese condominio y tipo de gasto.'
            )        

        # 3 Crear el Sub Tipo Gasto
        sub_tipo_gasto = SubTipoGasto.objects.create(
            condominio=condominio,
            tipo_gasto=tipo_gasto,            
            clave=clave,
            descripcion=descripcion,
            orden=orden,
            usuario_creo=administrador,            
        )
        
        
        return {
            "id": sub_tipo_gasto.id,
            "clave": sub_tipo_gasto.clave,
            "descripcion": sub_tipo_gasto.descripcion,
            "orden": sub_tipo_gasto.orden,                   
        }