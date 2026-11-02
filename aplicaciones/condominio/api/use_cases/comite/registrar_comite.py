from django.db import transaction
from django.utils import timezone


from ....models import Comite, ComiteIntegrante, Rol
from ....utilidades.validaciones import obtener_condominio_y_validar_administrador


class RegistrarComiteUseCase:

    @staticmethod
    
    @transaction.atomic
    def execute(
        *,
        administrador,        
        nombre,
        descripcion,
                       
    ):        

        # 1. Obtener el condominio del usuario y que tenga rol de administrador mediante la funcion
        condominio = obtener_condominio_y_validar_administrador(administrador)

        fecha_actual = timezone.localdate()
                
        # 2. Obtener los IDs de los comites a inactivar
        comite_ids = Comite.objects.filter(
            condominio=condominio, 
            activo=True
            ).values_list('id', flat=True)

        # 2.1. Inactivar los integrantes          
        ComiteIntegrante.objects.filter(
            comite_id__in=comite_ids,
            activo=True
        ).update(
            usuario_modifico=administrador,
            aplica_hasta=fecha_actual,
            activo=False,
            fecha_modificacion=timezone.now(),
        )

        # 2.2 Inactivar los comités
        Comite.objects.filter(
            id__in=comite_ids
        ).update(
            usuario_modifico=administrador,
            aplica_hasta=fecha_actual,
            activo=False,
            fecha_modificacion=timezone.now(),
        )        
                                       
        # 3 Crear el comité
        comite = Comite.objects.create(
            condominio=condominio,            
            nombre=nombre,
            descripcion=descripcion,            
            usuario_creo=administrador,
            aplica_desde=fecha_actual,
            ## aplica_hasta=None
        )

        # 4 Crear integrantes del comité solo con el administrador
        rol_administrador = Rol.objects.get(clave='ADMINISTRADOR')

        ComiteIntegrante.objects.create(
            condominio=condominio, 
            comite=comite,           
            usuario=administrador,
            rol=rol_administrador,            
            usuario_creo=administrador,  
            aplica_desde=fecha_actual,
            ## aplica_hasta=None          
        )

        
        # Regresar informacion de la creacion
        return {
            "id": comite.id,
            "nombre": comite.nombre,
        }