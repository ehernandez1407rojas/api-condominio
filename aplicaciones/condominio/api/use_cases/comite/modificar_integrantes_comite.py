from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError


from ....models import  ComiteIntegrante, Rol 
from ....utilidades.validaciones import obtener_condominio_y_validar_administrador, obtener_roles_y_condominio


class ModificarIntegrantesComiteUseCase:

    @staticmethod
    
    @transaction.atomic
    def execute(
        *,
        administrador,  
        comite,      
        miembros_quitar=None,
        miembros_agregar=None,
                       
    ):        

        # 1. Obtener el condominio del usuario y que tenga rol de administrador mediante la funcion
        condominio = obtener_condominio_y_validar_administrador(administrador)

        fecha_actual = timezone.localdate()

        # 2. Validar que al menos un arreglo tenga datos
        miembros_quitar = miembros_quitar or []
        miembros_agregar = miembros_agregar or []

        if not miembros_quitar and not miembros_agregar:
            raise ValidationError(
                "Debe enviar al menos un integrante para quitar o agregar."
            )

        # 3. Validar que el comite es del condominio del administrador
        if comite.condominio_id != condominio.id:
            raise ValidationError("El comité no pertenece a su condominio.")
        # 3.1 Validar que el comite este activo
        if not comite.activo:
            raise ValidationError(
                "No se pueden modificar los integrantes de un comité inactivo."
            )

        # 4. Ejecutar inactivaciones
        if miembros_quitar:
            # Opción A: Si la inactivación es por combinación específica de (usuario, rol)
            for item in miembros_quitar:
                usuario_id = item.get("usuario_id")
                rol_id = item.get("rol_id")                 
                
                #  Obtener el condominio del usuario y los roles que tiene  para validarlos      
                condominio_del_usuario, roles  = obtener_roles_y_condominio(usuario_id)   

                if condominio_del_usuario.id != condominio.id:
                    raise ValidationError(f"El usuario: {usuario_id} no pertenece al condominio.")

                # Validar que el usuario tenga actualmente ese rol
                # dentro de este comité
                if not ComiteIntegrante.objects.filter(
                    condominio=condominio,
                    comite=comite,
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    activo=True,
                ).exists():               
                    raise ValidationError(
                        "El usuario no tiene ese rol activo en el comité."
                    )
                  
                ComiteIntegrante.objects.filter(
                    condominio=condominio,
                    comite=comite,
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    activo=True,
                ).update(
                    activo=False,
                    aplica_hasta=fecha_actual,
                    usuario_modifico=administrador,
                    fecha_modificacion=timezone.now()
                )
        
        # 5. Agregar nuevos integrantes del comité
        #    Un miembro solo puede tener un rol activo en el comité.
        #    Si ya pertenece al comité, el administrador debe quitarlo
        #    antes de asignarle otro rol.       

        if miembros_agregar:
            # Solo roles permitidos para comité
            roles_permitidos = set(
                        Rol.objects.filter(
                            clave__in=['COMITE_VIGILANCIA', 'SECRETARIO']
                        ).values_list('id', flat=True)
                )   
            
            for item in miembros_agregar:
                usuario_id = item.get("usuario_id")
                rol_id = item.get("rol_id")

                #  Obtener el condominio del usuario y los roles que tiene  para validarlos      
                condominio_del_usuario, roles  = obtener_roles_y_condominio(usuario_id)   

                if condominio_del_usuario.id != condominio.id:
                    raise ValidationError(f"El usuario: {usuario_id} no pertenece al condominio.")

                if 'PROPIETARIO' not in roles:
                    raise ValidationError(f"El usuario no es PROPIETARIO, no puede ser miembro del comité.")    

                if ComiteIntegrante.objects.filter(
                    condominio=condominio,
                    comite=comite,
                    usuario_id=usuario_id,
                    activo=True,
                ).exists():
                    raise ValidationError(
                        "El propietario ya es miembro del comité, no puede tener más de un rol en el comité."
                    )                

                # Roles permitidos en el comité : COMITE_VIGILANCIA; SECRETARIO               
                if rol_id not in roles_permitidos:
                    raise ValidationError(
                        f"El rol {rol_id} no es valido para el comité."
                    )                                                                    

                # Crear los nuevos integrantes
                ComiteIntegrante.objects.create(
                    condominio=condominio,
                    comite=comite,
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    activo=True,
                    aplica_desde=fecha_actual,
                    usuario_creo=administrador,  
                )

        # Regresar informacion de la modificacion
        return {            
            "nombre": comite.nombre,
            "mensaje": "Modificación correcta de integrantes"
        }

