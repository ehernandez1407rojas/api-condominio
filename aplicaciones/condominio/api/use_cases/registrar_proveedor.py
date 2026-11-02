from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


from ...models import Proveedor, SituacionProveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador
# 👇 Import ABSOLUTO desde la raíz del proyecto
from infraestructure.decorators import manejar_unique_violation


class RegistrarProveedorUseCase:

    @staticmethod
    @transaction.atomic
    @manejar_unique_violation
    def execute(
        *,
        administrador,        
        nombre,
        direccion,
        celular=None,
        correo=None                   
    ):        

        # 1. Obtener el condominio del usuario y que tenga rol de administrador mediante la funcion
        condominio = obtener_condominio_y_validar_administrador(administrador)
        
                
        # 2. Validar que el celular no se repita en ese condominio        
        if celular is not None:
            existe_celular  = Proveedor.objects.filter(
                condominio=condominio,
                celular=celular            
            ).exists()

            if existe_celular:
                raise ValidationError(
                    f'Ya existe ese numero de celular en ese condominio.'
                )        

        # 3. Validar que el correo electronico no se repita en ese condominio
        if correo is not None:
            existe_correo  = Proveedor.objects.filter(
                condominio=condominio,
                correo=correo            
            ).exists()

            if existe_correo:
                raise ValidationError(
                    f'Ya existe ese correo en ese condominio.'
                ) 

        # 4 Asignar la situacion de PENDIENTE al crear el proveedor
        situacion_pendiente = SituacionProveedor.objects.filter(
            clave='PENDIENTE'                      
        ).first()
        
        if not situacion_pendiente:
            raise ValidationError("No existe la situación 'PENDIENTE' para asignarlo al proveedor")

        
        
        # 5 Crear el Proveedor
        proveedor = Proveedor.objects.create(
            condominio=condominio,            
            nombre=nombre,
            direccion=direccion,
            celular=celular, 
            correo=correo, 
            situacion= situacion_pendiente,
            usuario_creo=administrador,
            aplica_desde=timezone.localdate(),
            aplica_hasta=None

        )
        
        
        return {
            "id": proveedor.id,
            "nombre": proveedor.nombre,
            "direccion": proveedor.direccion,
            "celular": proveedor.celular,                   
        }