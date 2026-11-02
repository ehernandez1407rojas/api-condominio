from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

from ...models import GastoPagado
from ...utilidades.validaciones import obtener_roles_y_condominio
from ...api.constants import CONSERJE_PUEDE_PAGAR_GASTOS


class RegistrarGastoPagadoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        usuario,        
        tipo_gasto,
        sub_tipo_gasto=None,
        proveedor=None,
        importe_pagado,
        descripcion,
        fecha,
        gasto_comprobante=None
    ):        
    

        # 1. Obtener el condominio del usuario y los roles que tiene        
        condominio, roles  = obtener_roles_y_condominio(usuario)    

        roles_autorizados = ['ADMINISTRADOR']

        if CONSERJE_PUEDE_PAGAR_GASTOS:
            roles_autorizados += ['CONSERJE']

        if not any(rol in roles for rol in roles_autorizados):
            raise ValidationError(
                    'El usuario no tiene rol autorizado para registrar gastos y pagos.'
            )
                        
        # 2. Validar que el tipo de gasto exista y sea de ese condominio        
        if tipo_gasto.condominio_id != condominio.id:
            raise ValidationError(
                'El tipo de gasto no pertenece al condominio .'
            )

        # 3. Validar que el sub tipo de gasto exista y sea de ese condominio en caso de ser enviado             
        if sub_tipo_gasto is not None:                    
            if sub_tipo_gasto.condominio_id != condominio.id or sub_tipo_gasto.tipo_gasto_id != tipo_gasto.id:
                raise ValidationError(
                    'El sub tipo de gasto no pertenece al condominio  o al Tipo gasto.'
                )                                

        # 4. Validar que el proveedor exista y sea de ese condominio  en caso de ser enviado
        if proveedor is not None:                    
            if proveedor.condominio_id != condominio.id :
                raise ValidationError(
                    'El proveedor no pertenece al condominio .'
                )   

        # 5. Validar que la fecha de gasto no sea mayor a la del sistema     
        if not isinstance(fecha, date):
            raise ValidationError(
                'La fecha del gasto no es válida.'
            )       
        if fecha > timezone.localdate():
            raise ValidationError(
                'La fecha del gasto no puede ser mayor a la fecha actual.'
            )

        if importe_pagado <= 0:
            raise ValidationError(
                'El importe pagado debe ser mayor a cero.'
    )

        # 6 Iniciar variables de validacion  
        esta_autorizado=False       
        quien_autorizo=None
        cuando_autorizo=None
                
        
        # Validar si quien esta pagando es el  Admninistrador para autorizar tambien
        if 'ADMINISTRADOR' in roles: 
            esta_autorizado = True             
            quien_autorizo= usuario
            cuando_autorizo=timezone.localdate()
                                          
        
        # 8 Crear el Gasto Pagado
        gasto_pagado = GastoPagado.objects.create(
            condominio=condominio,            
            tipo_gasto=tipo_gasto,
            sub_tipo_gasto=sub_tipo_gasto,
            proveedor=proveedor,
            importe_pagado=importe_pagado,
            descripcion=descripcion,
            fecha=fecha,
            gasto_comprobante=gasto_comprobante,
            esta_autorizado=esta_autorizado,
            quien_autorizo=quien_autorizo ,
            cuando_autorizo=cuando_autorizo,
            usuario_creo=usuario           

        )
        
        
        return {
            "tipo_gasto": gasto_pagado.tipo_gasto.clave,         
            "descripcion": gasto_pagado.descripcion,
            "importe": gasto_pagado.importe_pagado
                              
        }