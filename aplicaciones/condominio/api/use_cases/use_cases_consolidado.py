# ==========================================================
# ARCHIVO CONSOLIDADO DE USE CASES
# ==========================================================

# ======================================================================
# ARCHIVO: actualizar_proveedor.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\actualizar_proveedor.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import Proveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarProveedorUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        proveedor_id,
        **campos_a_actualizar
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )
        
        # 2. Validar que haya enviado al menos un campo a actualizar
        if not campos_a_actualizar:            
            raise ValidationError(
                'Debe indicar al menos un campo para actualizar.'
            )

        # 3. Obtener el Proveedor del condominio y bloquear la fila
        proveedor = Proveedor.objects.select_for_update().filter(
            pk=proveedor_id,
            condominio=condominio
        ).first()

        if not proveedor:
            raise ValidationError(
                'Este proveedor no existe en el condominio.'
            )

        # 4. Validar celular que no se repita en otro proveedor  si se desea modificar
        celular = campos_a_actualizar.get('celular')
        
        if celular is not None:
            existe_proveedor = Proveedor.objects.filter(
                condominio=condominio,
                celular=celular
            ).exclude(
                pk=proveedor.pk
            ).exists()

            if existe_proveedor:
                raise ValidationError(
                    'Ya existe otro proveedor con ese celular '
                    'en el condominio.'
                )
            
        # 5. Validar correo que no se repita en otro proveedor  si se desea modificar
        correo = campos_a_actualizar.get('correo')

        if correo is not None:
            existe_proveedor = Proveedor.objects.filter(
                condominio=condominio,
                correo=correo
            ).exclude(
                pk=proveedor.pk
            ).exists()

            if existe_proveedor:
                raise ValidationError(
                    'Ya existe otro proveedor con ese correo '
                    'en el condominio.'
                )

        # 6. Actualizar únicamente los campos enviados y la auditoria        

        for clave, valor in campos_a_actualizar.items():            
            setattr(proveedor, clave, valor)

        proveedor.usuario_modifico = administrador

        # 7. Guardar cambios
        campos_a_guardar = list(campos_a_actualizar.keys())+['usuario_modifico', 'fecha_modificacion']
        proveedor.save(
            update_fields=campos_a_guardar
        )

        # 8. Respuesta
        return {
            "id": proveedor.id,
            "nombre": proveedor.nombre,
            "direccion": proveedor.direccion,
            "celular": proveedor.celular,  
        }


# ======================================================================
# ARCHIVO: actualizar_situacion_proveedor.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\actualizar_situacion_proveedor.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import Proveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarSituacionProveedorUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        proveedor_id,
        situacion_proveedor
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )               

        # 2. Obtener el Proveedor del condominio y bloquear la fila
        proveedor = Proveedor.objects.select_for_update().filter(
            pk=proveedor_id,
            condominio=condominio
        ).first()

        if not proveedor:
            raise ValidationError(
                'Este proveedor no existe en el condominio.'
            )        

        # 3. Actualizar la situacion del proveedor y los campos de auditoria                
        proveedor.usuario_modifico = administrador
        proveedor.situacion = situacion_proveedor
        
        proveedor.save(update_fields=[ 'situacion', 'usuario_modifico', 'fecha_modificacion'])
        

        # 5. Respuesta
        return {            
            "nombre": proveedor.nombre,
            "situacion": proveedor.situacion.clave,             
        }


# ======================================================================
# ARCHIVO: actualizar_sub_tipo_gasto.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\actualizar_sub_tipo_gasto.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import SubTipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarSubTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        sub_tipo_gasto_id,            
        clave=None,
        descripcion=None,
        orden=None
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        # 2. Validar que se haya enviado al menos un campo
        # Genero un diccionario
        campos = {
            'clave': clave,
            'descripcion': descripcion,
            'orden': orden,
        }


        if not any(valor is not None for valor in campos.values()):            
            raise ValidationError(
                'Debe indicar al menos un campo para actualizar.'
            )

        # 3. Obtener el SubTipoGasto del condominio y bloquear la fila
        sub_tipo_gasto = SubTipoGasto.objects.select_for_update().filter(
            pk=sub_tipo_gasto_id,
            condominio=condominio
        ).first()

        if not sub_tipo_gasto:
            raise ValidationError(
                'Ese sub tipo de gasto no existe en el condominio.'
            )

        # 4. Validar clave en caso de que se desea modificar
        if clave is not None:
            existe_sub_tipo_gasto = SubTipoGasto.objects.filter(
                condominio=condominio,
                tipo_gasto=sub_tipo_gasto.tipo_gasto,
                clave=clave
            ).exclude(
                pk=sub_tipo_gasto.pk
            ).exists()

            if existe_sub_tipo_gasto:
                raise ValidationError(
                    'Ya existe un sub tipo de gasto con esa clave '
                    'en el condominio.'
                )

        # 5. Actualizar únicamente los campos enviados y la auditoria
        if clave is not None:
            sub_tipo_gasto.clave = clave

        if descripcion is not None:
            sub_tipo_gasto.descripcion = descripcion

        if orden is not None:
            sub_tipo_gasto.orden = orden

        sub_tipo_gasto.usuario_modifico = administrador

        # 6. Guardar cambios
        sub_tipo_gasto.save(
            update_fields=['clave', 'descripcion', 'orden', 'usuario_modifico', 'fecha_modificacion']
        )

        # 6. Respuesta
        return {
            "id": sub_tipo_gasto.id,
            "clave": sub_tipo_gasto.clave,
            "descripcion": sub_tipo_gasto.descripcion,
            "orden": sub_tipo_gasto.orden,
        }


# ======================================================================
# ARCHIVO: actualizar_tipo_gasto.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\actualizar_tipo_gasto.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import TipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class ActualizarTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        tipo_gasto_id,
        clave=None,
        descripcion=None,
        orden=None
    ):

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        # 2. Validar que se haya enviado al menos un campo
        # Genero un diccionario
        campos = {
            'clave': clave,
            'descripcion': descripcion,
            'orden': orden,
        }


        if not any(valor is not None for valor in campos.values()):            
            raise ValidationError(
                'Debe indicar al menos un campo para actualizar.'
            )

        # 3. Obtener el TipoGasto del condominio y bloquear la fila
        tipo_gasto = TipoGasto.objects.select_for_update().filter(
            pk=tipo_gasto_id,
            condominio=condominio
        ).first()

        if not tipo_gasto:
            raise ValidationError(
                'Ese tipo de gasto no existe en el condominio.'
            )

        # 4. Validar clave si se desea modificar
        if clave is not None:
            existe_tipo_gasto = TipoGasto.objects.filter(
                condominio=condominio,
                clave=clave
            ).exclude(
                pk=tipo_gasto.pk
            ).exists()

            if existe_tipo_gasto:
                raise ValidationError(
                    'Ya existe un tipo de gasto con esa clave '
                    'en el condominio.'
                )

        # 5. Actualizar únicamente los campos enviados y la auditoria
        if clave is not None:
            tipo_gasto.clave = clave

        if descripcion is not None:
            tipo_gasto.descripcion = descripcion

        if orden is not None:
            tipo_gasto.orden = orden

        tipo_gasto.usuario_modifico = administrador

        # 6. Guardar cambios
        tipo_gasto.save(
            update_fields=['clave', 'descripcion', 'orden', 'usuario_modifico', 'fecha_modificacion']
        )

        # 6. Respuesta
        return {
            "id": tipo_gasto.id,
            "clave": tipo_gasto.clave,
            "descripcion": tipo_gasto.descripcion,
            "orden": tipo_gasto.orden,
        }


# ======================================================================
# ARCHIVO: autorizar_gasto_pagado.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\autorizar_gasto_pagado.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


from ...models import   GastoPagado
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class AutorizarGastoPagadoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,                
        gasto_pagado_id,        
                    
    ):        

        # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )       
                                
        # 2. Obtener el registro del Gasto Pagado  del condominio y bloquear la fila
        gasto_pagado = GastoPagado.objects.select_for_update().filter(
            pk=gasto_pagado_id,
            condominio=condominio
            ).first()
        
        if not gasto_pagado:
            raise ValidationError(
                'Este Gasto Pagado no existe en el condominio.'
            ) 

        # 3. Validar que el gasto pagado no este cancelado
        if gasto_pagado.esta_cancelado:
            raise ValidationError(
                'Este Gasto Pagado está cancelado y no puede ser autorizado.'
            )

        if gasto_pagado.esta_autorizado:
            raise ValidationError(
                'Este Gasto Pagado ya está autorizado.'
            )

        # 4 Autorizar el gasto pagado
        
        fecha_autorizacion = timezone.localdate() ## timezone.now().date() 

        gasto_pagado.esta_autorizado = True
        gasto_pagado.quien_autorizo = administrador
        gasto_pagado.cuando_autorizo = fecha_autorizacion
        gasto_pagado.usuario_modifico = administrador

        
        gasto_pagado.save(
            update_fields=[
                'esta_autorizado',
                'quien_autorizo',
                'cuando_autorizo',
                'usuario_modifico',
                'fecha_modificacion'
            ]
        )

        return {
            "descripcion": gasto_pagado.descripcion,
            "fecha": gasto_pagado.cuando_autorizo           
                    
        }


# ======================================================================
# ARCHIVO: cambiar_password.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\cambiar_password.py
# ======================================================================

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class CambiarPasswordUseCase:

    @staticmethod
    def execute(user, password_actual, password_nueva):

        # 1. Validar password actual
        if not user.check_password(password_actual):
            raise ValidationError({
                'password_actual': 'La contraseña actual no es correcta.'
            })

        # 2. Validar nueva password con los validadores de Django
        try:
            validate_password(password_nueva, user)
        except ValidationError as e:
            raise ValidationError({
                'password_nueva': e.messages
            })

        # 3. Cambiar password
        user.set_password(password_nueva)
        user.save(update_fields=['password'])

        return user


# ======================================================================
# ARCHIVO: cancelar_cuota.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\cancelar_cuota.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ...models import   Cuota,  UsuarioRol,  CuotaExigible, TipoCuota


class CancelarCuotaUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,        
        cuota,
        comentario_cancelacion
                     
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
                
        # 3. Validar que la cuota pertenezca al condominio del administrador  y que la cuota este activa
        # 
        if cuota.condominio != condominio:
            raise ValidationError(
                'La cuota que se quiere cancelar no pertenece al condominio.'
            )

        if not cuota.activo:
            raise ValidationError(
                'La cuota que se quiere cancelar ya está inactiva.'
        )      

        ## ya se tiene la instancia de la cuota no se necesita consultar
        """ 
        cuota_del_condominio = Cuota.objects.filter(
            condominio=condominio,
            cuota=cuota,
            activo=True
        ).exists()

        if not cuota_del_condominio:
            raise ValidationError(
                f'La cuota que se quiere cancelar no es del condominio.'
            )
        """
        # 4 Cancelar la cuota Estado a Falso y Fecha hasta con la del sistema

        fecha_cancelacion = timezone.localdate() ## timezone.now().date() 

        cuota.activo = False
        cuota.aplica_hasta = fecha_cancelacion
        cuota.comentario_cancelacion = comentario_cancelacion
        cuota.usuario_modifico=administrador
        cuota.save(
            update_fields=[
                'activo',
                'aplica_hasta',
                'comentario_cancelacion',
                'usuario_modifico',
                'fecha_modificacion'
            ]
        )
                
       
        # 5 Marcar como canceladas las exigibilidades que sean exigibles a partir del proximo mes de la cuota que se cancela 
        # Si hoy es 15-09-2026, esto generará la fecha 2026-10-01
        proximo_mes_dia_uno = (fecha_cancelacion + relativedelta(months=1)).replace(day=1)

        # Filtrar y actualizar en una sola consulta
        cuotas_exigibles_canceladas  = CuotaExigible.objects.filter(
        condominio = condominio,
        cuota=cuota,  
        estado='E',
        fecha_exigibilidad__gte=proximo_mes_dia_uno
        ).update(            
            estado='C',
            fecha_modificacion=timezone.now(),
        )
               

        return {
            "nombre": cuota.nombre,
            "tipo_cuota": cuota.tipo_cuota.clave,
            "cuotas_exigibles_canceladas": cuotas_exigibles_canceladas 
           
        }


# ======================================================================
# ARCHIVO: cancelar_gasto_pagado.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\cancelar_gasto_pagado.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ...utilidades.validaciones import obtener_condominio_y_validar_administrador
from ...models import   GastoPagado


class CancelarGastoPagadoUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,        
        gasto_pagado_id,
        motivo_cancelacion
                     
    ):        

       # 1. Validar administrador y obtener condominio
        condominio = obtener_condominio_y_validar_administrador(
            administrador
        )

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )       
                               
        # 2. Obtener el registro del Gasto Pagado  del condominio y bloquear la fila
        gasto_pagado = GastoPagado.objects.select_for_update().filter(
            pk=gasto_pagado_id,
            condominio=condominio
            ).first()
        
        if not gasto_pagado:
            raise ValidationError(
                'Este Gasto Pagado no existe en el condominio.'
            ) 

        # 3. Validar que el gasto pagado no este cancelado
        if gasto_pagado.esta_cancelado:
            raise ValidationError(
                            'Este Gasto Pagado no se puede volver a cancelar.'
                        ) 

                         
        # 4 Cancelar el gasto pagado

        fecha_cancelacion = timezone.localdate() ## timezone.now().date() 

        gasto_pagado.esta_cancelado = True
        gasto_pagado.quien_cancelo = administrador
        gasto_pagado.cuando_cancelo = fecha_cancelacion
        gasto_pagado.motivo_cancelacion = motivo_cancelacion
        gasto_pagado.usuario_modifico=administrador
        gasto_pagado.save(
            update_fields=[
                'esta_cancelado',
                'quien_cancelo',
                'cuando_cancelo',
                'motivo_cancelacion',
                'usuario_modifico',
                'fecha_modificacion'
            ]
        )
                
       
        # 5. Datos de respuesta

        return {
            "gasto": gasto_pagado.descripcion,
            "motivo_cancelacion": gasto_pagado.motivo_cancelacion,
            "fecha": gasto_pagado.cuando_cancelo 
           
        }


# ======================================================================
# ARCHIVO: cobrar_cuota.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\cobrar_cuota.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta

from ...models import   UsuarioRol,   CuotaExigible,  CuotaCobrada
from ..constants import  MESES_EXIGIBLES_POSTERIORES_HOY


class CobrarCuotaUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador_conserje,        
        propiedad,
        cuota_exigible,
        importe_cobrado,
        descripcion_comprobante
                    
    ):        

        # 1. Validar que el usuario tenga condominio -- Obtener el condominio del usuario que cobra.
        condominio = administrador_conserje.condominio

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )
        
        # 2. Validar que el usuario pueda cobrar -- Validar que el usuario tenga rol de ADMINISTRADOR o CONSERJE activo 
        es_administrador_conserje = UsuarioRol.objects.filter(            
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=timezone.localdate()),
            usuario=administrador_conserje,            
            condominio=condominio,
            rol__clave__in=['ADMINISTRADOR', 'CONSERJE'],
            activo=True
            ).first()

        if not es_administrador_conserje:
            raise ValidationError(
                'El usuario no es ni administrador ni conserje no puede cobrar la cuota.'
        )

        rol = es_administrador_conserje.rol.clave

        # 3 Validar la propiedad -- que se recibe debe pertenecer al condominio del usuario que cobra
        if not propiedad.condominio == condominio:
            raise ValidationError(
                    'La propiedad no pertenece al condominio de quien esta cobrando.'
                )

                        
        # 4. Validar la cuota exigible -- Validar que la cuota exigible que se va a cobrar sea la mas antigua en estado EXIGIBLE = 'E'    
        # y que sea del mismo tipo de cuota

        if cuota_exigible.estado != 'E':
            raise ValidationError(
                'La cuota exigible no se encuentra pendiente de cobro.'
            )

        tipo_cuota = cuota_exigible.cuota.tipo_cuota.clave          

        cuota_exigible_anterior_tipo = CuotaExigible.objects.filter(
            condominio=condominio,
            propiedad=propiedad,
            estado='E',
            cuota__tipo_cuota__clave=tipo_cuota,
            fecha_exigibilidad__lt=cuota_exigible.fecha_exigibilidad
        ).order_by('fecha_exigibilidad').first()
        
        if cuota_exigible_anterior_tipo :
            raise ValidationError(
                f'Existe una cuota anterior pendiente del mismo tipo, primero se debe cobrar la anterior: {cuota_exigible_anterior_tipo.id} {cuota_exigible_anterior_tipo.fecha_exigibilidad}'
            )

        # validar la prelacion entre tipo de cuota ORDINARIA vs EXTRAORDINARIA
        if tipo_cuota == 'EXTRAORDINARIA':
            cuota_ordinaria = CuotaExigible.objects.filter(
            propiedad=propiedad,
            estado='E',
            cuota__tipo_cuota__clave='ORDINARIA',
            fecha_exigibilidad=cuota_exigible.fecha_exigibilidad
        ).first()

            if cuota_ordinaria:
                raise ValidationError(
                    'No se puede cobrar la cuota extraordinaria porque existe una cuota ordinaria pendiente del mismo mes.'
                )
        

        # 5. Validar la ventana de cobro -- La fecha de exigibilidad debe estar dentro de del mes actual y dos meses
        # siempre que se siga la prelación por orden de fecha

        hoy = timezone.localdate()
        fecha_mas_meses = hoy + relativedelta(months=+MESES_EXIGIBLES_POSTERIORES_HOY)
        ultimo_dia_dos_meses = fecha_mas_meses + relativedelta(day=31)

        if cuota_exigible.fecha_exigibilidad > ultimo_dia_dos_meses:
            raise ValidationError(
                'No esta permitido cobrar cuotas mayores a dos mes de la fecha actual'
            )
       

        # 6. Validar el importe cobrado
        if importe_cobrado <=0:
            raise ValidationError(
                    'El importe a cobrar debe ser mayor a cero'
                )

        # 6.1. Determinar si es el primer cobro de esa exigibilidad
        cuota_pendiente_cobro = CuotaCobrada.objects.filter(
                cuota_exigible=cuota_exigible
            ).order_by('-id').first()

        # 7. Determinar el saldo a favor de la exigibilidad inmediatamente anterior del ultimo cobro efectuado
        # -- Determinar si hay saldo a favor de la cuota_exigible anterior de esa cuota
        
        # Encontrar Cuota exigible inmediata anterior
        cuota_exigible_anterior = CuotaExigible.objects.filter(
            propiedad=propiedad,
            cuota=cuota_exigible.cuota,
            fecha_exigibilidad__lt=cuota_exigible.fecha_exigibilidad,
        ).order_by('-fecha_exigibilidad').first()

        # Buscar el ultimo cobro de esa exigibilidad se inicializa
        ultimo_cobro_anterior = None

        # Buscar el ultimo cobro de esa exigibilidad
        if cuota_exigible_anterior:
            ultimo_cobro_anterior = CuotaCobrada.objects.filter(
                cuota_exigible=cuota_exigible_anterior
            ).order_by('-id').first()

        # Determinar el saldo anterior
        if ultimo_cobro_anterior:
            saldo_anterior = ultimo_cobro_anterior.saldo
        else:
            saldo_anterior = 0

        # 8. Determinar el saldo a favor.
        saldo_favor = 0

        if saldo_anterior < 0:
            saldo_favor = saldo_anterior


        # 9. Crear el cobro
        # Iniciar variables de validacion 
        administrador_valido = None
        hoy_valido = None
        ya_esta_validada = False
        comentario_validacion = None


        # Validar si quien esta cobrando es el  Admninistrador 
        if rol == 'ADMINISTRADOR':            
            administrador_valido= administrador_conserje
            hoy_valido=timezone.now()
            ya_esta_validada = True 
            comentario_validacion='ADMINISTRADOR COBRO'       

        # cobrar la cuota         
        if not cuota_pendiente_cobro:
            saldo = cuota_exigible.importe_cuota + saldo_favor - importe_cobrado
        else:
            saldo = cuota_pendiente_cobro.saldo - importe_cobrado  

        cuota_cobrada = CuotaCobrada.objects.create(
            condominio=condominio,
            propiedad=propiedad,                
            cuota_exigible=cuota_exigible,
            importe_exigible=cuota_exigible.importe_cuota,
            quien_recibe=administrador_conserje,
            importe_cobrado=importe_cobrado,
            comprobante=descripcion_comprobante,
            quien_valido=administrador_valido,
            cuando_valido=hoy_valido,
            esta_validada=ya_esta_validada,
            saldo=saldo,
            comentario_validacion=comentario_validacion,
            usuario_creo=administrador

        )

    
        # 10. Determinar estado de exigibilidad
        if cuota_cobrada.saldo <= 0:
            cuota_exigible.estado = 'P'
            cuota_exigible.usuario_modifico
            cuota_exigible.save(update_fields=['estado','usuario_modifico', 'fecha_modificacion'])

        return {
            "propiedad": propiedad.nombre,
            "importe_cobrado": importe_cobrado
                    
        }


# ======================================================================
# ARCHIVO: definir_cuota.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\definir_cuota.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta

from ...models import TipoCuota,  Cuota,  UsuarioRol,  Propiedad, CuotaExigible, Condominio, Usuario


class DefinirCuotaUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,        
        tipo_cuota,
        nombre,
        importe,
        aplica_desde,
        aplica_hasta,             
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
                
        # 3. Validar los datos de la cuota y validarlos contra las reglas de negocio        

        existe_cuota_activa = Cuota.objects.filter(
            condominio=condominio,
            tipo_cuota=tipo_cuota,
            activo=True
        ).exists()

        if existe_cuota_activa:
            raise ValidationError(
                f'Ya existe una cuota {tipo_cuota.clave} activa en ese condominio.'
            )

        # 4 Validar las fechas  desde y hasta de la cuota a definir
                
        if aplica_hasta < aplica_desde:            
            raise ValidationError(
                f'La fecha fin de aplicacion de la cuota, {aplica_hasta} no puede ser menor a la fecha inicio,  {aplica_desde} '
            )

        # 5 Crear la cuota
        cuota = Cuota.objects.create(
            condominio=condominio,
            tipo_cuota=tipo_cuota,
            nombre=nombre,
            importe=importe,
            aplica_desde=aplica_desde,
            aplica_hasta=aplica_hasta,
            usuario_creo=administrador
        )

        # 6 Obtener las propiedades registradas del condominio para generar los exigibles

        propiedades = Propiedad.objects.filter(
            condominio=condominio
        )

        # 7 Generar las fechas de exigibilidad validando previamente si existe alguna propiedad        
        
        fechas_exigibilidad = []
        fecha_exigible_inicio = aplica_desde.replace(day=1)
        frecuencia = tipo_cuota.frecuencia_cuota.clave        

        if frecuencia == 'MENSUAL':
            while fecha_exigible_inicio <= aplica_hasta:
                fechas_exigibilidad.append(fecha_exigible_inicio)
                fecha_exigible_inicio += relativedelta(months=1)

        elif frecuencia == 'UNICA':
            fechas_exigibilidad.append(fecha_exigible_inicio)

        # 8 Generar las cuotas exigibles                    
        cuotas_exigibles = []

        for propiedad in propiedades:
            for fecha in fechas_exigibilidad:
                cuotas_exigibles.append(
                    CuotaExigible(
                        condominio=condominio,
                        propiedad = propiedad,
                        cuota = cuota,
                        fecha_exigibilidad = fecha,
                        importe_cuota = cuota.importe,    
                        usuario_creo=administrador                    
                    )
                )

        # Insertar todas las exigibilidades en una transaccion
        
        CuotaExigible.objects.bulk_create(cuotas_exigibles)
        

        return {
            "nombre": cuota.nombre,
            "tipo_cuota": tipo_cuota.clave,
            "cuotas_exigibles": len(cuotas_exigibles)           
        }


# ======================================================================
# ARCHIVO: establecer_password_con_token.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\establecer_password_con_token.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password  # 👈 Importar
from django.utils import timezone
import hashlib

from ...models import (    Usuario,        TipoToken,    TokenUsuario,    )


class EstablecerPasswordConTokenUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        token,
        nuevo_password,               
    ):

        # 1. Validar que el token exista y sea válido
        try:
            token_obj = TokenUsuario.objects.get(
                token_hash=hashlib.sha256(str(token).encode('utf-8')).hexdigest(),
                fecha_cancelacion__isnull=True,
                fecha_uso__isnull=True,
                fecha_expiracion__gt=timezone.now(),                
            )
            
            usuario = token_obj.usuario
            
        except TokenUsuario.DoesNotExist:
            raise ValidationError(
                'El token no es válido o ya no está disponible para su uso.'
            )

        # 2. Validar la nueva contraseña con Django (usando tu configuración de settings.py)
        try:
            validate_password(nuevo_password, usuario)
        except ValidationError as e:
            # Re-lanzar con el formato esperado
            raise ValidationError({
                'password': e.messages
            })

        # 3. Establecer nuevo password
        usuario.set_password(nuevo_password)       
        usuario.save(update_fields=["password"]) 
        
        # 4. Marcar token como utilizado
        token_obj.fecha_uso = timezone.now()
        token_obj.usuario_modifico=usuario
        token_obj.save(update_fields=["fecha_uso","usuario_modifico", "fecha_modificacion"])

        # 5. Retornar respuesta
        return {
            "mensaje": "Contraseña establecida correctamente",
            "usuario": usuario.email_whatsapp,
        }


# ======================================================================
# ARCHIVO: generar_token.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\generar_token.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import hashlib

from datetime import timedelta
import secrets

from ...models import (
    Usuario,    
    TipoToken,
    TokenUsuario,    
)

class GenerarTokenUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        tipo_token,        
    ):

        # 1. Obtener el condominio del administrador.
        condominio = administrador.condominio

        if not condominio:
            raise ValidationError(
                'El usuario administrador no tiene un condominio asignado.'
            )
        
        # 2. verifica que el usuario exista con ese correo/whatsapp.
        usuario = Usuario.objects.filter(
            email_whatsapp=email_whatsapp
        ).first()

        # 3. Crear el token temporal.
        #    Si existe un token vigente del mismo tipo, se cancela antes de generar el nuevo.
        
        if usuario :

            tipo_token_obj = TipoToken.objects.get(
                    clave=tipo_token
                )
            fecha_hora_actual=timezone.now()

            token_vigente = TokenUsuario.objects.filter(
                    usuario=usuario,
                    tipo=tipo_token_obj,
                    fecha_uso__isnull=True,
                    fecha_cancelacion__isnull=True,
                    fecha_expiracion__gt=fecha_hora_actual,
                ).first()

            if token_vigente :
                token_vigente.fecha_cancelacion = fecha_hora_actual
                token_vigente.usuario_modifico=usuario
                token_vigente.save(update_fields=["fecha_cancelacion", "usuario_modifico", "fecha_modificacion"])

            token_temporal = secrets.randbelow(900000) + 100000
            token_hash = hashlib.sha256(str(token_temporal).encode('utf-8')).hexdigest()                        

            token_usuario = TokenUsuario.objects.create(
                condominio=condominio,
                usuario=usuario,
                token_hash=token_hash,
                tipo=tipo_token_obj,
                fecha_generacion= fecha_hora_actual,
                fecha_expiracion = (
                        fecha_hora_actual
                                + timedelta(minutes=tipo_token_obj.duracion_minutos) ),                            
                usuario_creo=administrador,
            )
            
        # 3.1. El usuario no existe.
        else:
            raise ValidationError(
                'El usuario no existe.'
            )

        # 4 regresa el usuario token temporal
        return {
             "token": token_temporal           
        }


# ======================================================================
# ARCHIVO: registra_conserje_con_token.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registra_conserje_con_token.py
# ======================================================================

# nuevo archivo: registrar_propietario_con_token.py
from django.db import transaction
from django.core.exceptions import ValidationError

from .registrar_conserje import RegistrarConserjeUseCase
from .generar_token import GenerarTokenUseCase


class RegistrarConserjeConTokenUseCase:
    """Orquesta el registro del conserje y generación de token"""
    
    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,
        
    ):
        # 1. Registrar al conserje
        try:
            resultado_registro = RegistrarConserjeUseCase.execute(
                        administrador=administrador,
                        email_whatsapp=email_whatsapp,
                        nombre_completo=nombre_completo,
                        
                    )
        except ValidationError as e:
            # si falla la creacion del conserje, se sale de la transaccion
            raise ValidationError(
                f"Error al crear conserje: {e.messages}"
            )            
        
                
        # 2. Generar token para establecer contraseña
        try:
            resultado_token = GenerarTokenUseCase.execute(
                administrador=administrador,
                email_whatsapp=email_whatsapp,
                tipo_token='REGISTRO_CONSERJE',
            )
        except ValidationError as e:
            # Si falla la generación del token, la transacción hace rollback
            raise ValidationError(
                f"Error al generar token: {e.messages}"
            )
        
        # 3. Combinar resultados
        
        return {
            **resultado_registro,
            "token_temporal": resultado_token["token"],
            "mensaje": "Conserje registrado. Token generado para establecer contraseña."
        }


# ======================================================================
# ARCHIVO: registra_propietario_con_token.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registra_propietario_con_token.py
# ======================================================================

# nuevo archivo: registrar_propietario_con_token.py
from django.db import transaction
from django.core.exceptions import ValidationError

from .registrar_propietario import RegistrarPropietarioUseCase
from .generar_token import GenerarTokenUseCase


class RegistrarPropietarioConTokenUseCase:
    """Orquesta el registro de propietario y generación de token"""
    
    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,
        nombre_propiedad,
        direccion,
    ):
        # 1. Registrar al propietario
        resultado_registro = RegistrarPropietarioUseCase.execute(
            administrador=administrador,
            email_whatsapp=email_whatsapp,
            nombre_completo=nombre_completo,
            nombre=nombre_propiedad,
            direccion=direccion,
        )
        
        # 2. Generar token para establecer contraseña
        try:
            resultado_token = GenerarTokenUseCase.execute(
                administrador=administrador,
                email_whatsapp=email_whatsapp,
                tipo_token='REGISTRO_PROPIETARIO',
            )
        except ValidationError as e:
            # Si falla la generación del token, la transacción hace rollback
            raise ValidationError(
                f"Error al generar token: {e.messages}"
            )
        
        # 3. Combinar resultados
        
        return {
            **resultado_registro,
            "token_temporal": resultado_token["token"],
            "mensaje": "Propietario registrado. Token generado para establecer contraseña."
        }


# ======================================================================
# ARCHIVO: registrar_comentario_proveedor.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_comentario_proveedor.py
# ======================================================================

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


# ======================================================================
# ARCHIVO: registrar_condominio.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_condominio.py
# ======================================================================

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
        condominio.usuario_modifico=usuario
        condominio.save(update_fields=["usuario_creo","usuario_modifico", "fecha_modificacion"])

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


# ======================================================================
# ARCHIVO: registrar_conserje.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_conserje.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from ...models import (
    Usuario,
    UsuarioRol,
    Rol,    
)

class RegistrarConserjeUseCase:

    @staticmethod
    @transaction.atomic
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
        rol_propietario = Rol.objects.get(
            clave="CONSERJE"
        )

        # 4.1. Buscar si ya tiene el rol CONSERJE activo.
        usuario_rol = UsuarioRol.objects.filter(
            condominio=condominio,
            usuario=usuario,
            rol=rol_propietario,
            activo=True
        ).first()

        # 4.2. Crear la relación si no existe.
        if usuario_rol is None:
            usuario_rol = UsuarioRol.objects.create(
                condominio=condominio,
                usuario=usuario,
                rol=rol_propietario,
                usuario_creo=administrador,
            )        

        return {            
            "usuario": usuario,
            "usuario_rol": usuario_rol,
        }


# ======================================================================
# ARCHIVO: registrar_gasto_pagado.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_gasto_pagado.py
# ======================================================================

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


# ======================================================================
# ARCHIVO: registrar_propietario.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_propietario.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from ...models import (
    Usuario,
    UsuarioRol,
    Rol,
    Propiedad,
)

class RegistrarPropietarioUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,
        email_whatsapp,
        nombre_completo,
        nombre,
        direccion,
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

        # 3. Buscar al usuario por email_whatsapp.
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

        # 4. Obtener el ID rol de PROPIETARIO.
        rol_propietario = Rol.objects.get(
            clave="PROPIETARIO"
        )

        # 4.1. Buscar si ya tiene el rol PROPIETARIO activo.
        usuario_rol = UsuarioRol.objects.filter(
            condominio=condominio,
            usuario=usuario,
            rol=rol_propietario,
            activo=True
        ).first()

        # 4.2. Crear la relación si no existe.
        if usuario_rol is None:
            usuario_rol = UsuarioRol.objects.create(
                condominio=condominio,
                usuario=usuario,
                rol=rol_propietario,
                usuario_creo=administrador,
            )

        # 5. Crear la propiedad para ese usuario.
        propiedad = Propiedad.objects.create(
            nombre=nombre,
            direccion=direccion,
            condominio=condominio,
            propietario=usuario,
            usuario_creo=administrador,
        )

        

        return {
            "propiedad": propiedad,
            "usuario": usuario,
            "usuario_rol": usuario_rol,
        }


# ======================================================================
# ARCHIVO: registrar_proveedor.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_proveedor.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


from ...models import Proveedor, SituacionProveedor
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class RegistrarProveedorUseCase:

    @staticmethod
    @transaction.atomic
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


# ======================================================================
# ARCHIVO: registrar_sub_tipo_gasto.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_sub_tipo_gasto.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import  SubTipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class RegistrarSubTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
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


# ======================================================================
# ARCHIVO: registrar_tipo_gasto.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\registrar_tipo_gasto.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError


from ...models import TipoGasto
from ...utilidades.validaciones import obtener_condominio_y_validar_administrador


class RegistrarTipoGastoUseCase:

    @staticmethod
    @transaction.atomic
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


# ======================================================================
# ARCHIVO: reiniciar_password.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\reiniciar_password.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import hashlib

from datetime import timedelta
import secrets

from ...models import (
    Usuario,    
    TipoToken,
    TokenUsuario,    
)

class ReiniciarPasswordUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,        
        email_whatsapp,               
    ):
        
        
        # 1. verifica que el usuario exista con ese correo/whatsapp.
        usuario = Usuario.objects.filter(
            email_whatsapp=email_whatsapp
        ).first()

        # 3. Crear el token temporal.
        #    Si existe un token vigente del mismo tipo, se cancela antes de generar el nuevo.        
        if usuario :
            tipo_token='REINICIO_CONTRASEÑA'
            tipo_token_obj = TipoToken.objects.get(
                    clave=tipo_token
                )
            fecha_hora_actual=timezone.now()

            token_vigente = TokenUsuario.objects.filter(
                    usuario=usuario,
                    tipo=tipo_token_obj,
                    fecha_uso__isnull=True,
                    fecha_cancelacion__isnull=True,
                    fecha_expiracion__gt=fecha_hora_actual,
                ).first()

            if token_vigente :
                token_vigente.fecha_cancelacion = fecha_hora_actual
                token_vigente.usuario_modifico=usuario
                token_vigente.save(update_fields=["fecha_cancelacion", "usuario_modifico", "fecha_modificacion"])

            token_temporal = secrets.randbelow(900000) + 100000
            token_hash = hashlib.sha256(str(token_temporal).encode('utf-8')).hexdigest()                        

            token_usuario = TokenUsuario.objects.create(
                condominio=usuario.condominio,
                usuario=usuario,
                token_hash=token_hash,
                tipo=tipo_token_obj,
                fecha_generacion= fecha_hora_actual,
                fecha_expiracion = (
                        fecha_hora_actual
                                + timedelta(minutes=tipo_token_obj.duracion_minutos) ),                            
                usuario_creo=usuario,
            )
            
        # 3.1. El usuario no existe.
        else:
            raise ValidationError(
                'El usuario no existe.'
            )

        # 4 regresa el usuario token temporal
        return {
             "token": token_temporal           
        }


# ======================================================================
# ARCHIVO: validar_cobro.py
# RUTA: C:\python_311\api-condominio\aplicaciones\condominio\api\use_cases\validar_cobro.py
# ======================================================================

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import date

from ...models import     CuotaCobrada, UsuarioRol


class ValidarCobroUseCase:

    @staticmethod
    @transaction.atomic
    def execute(
        *,
        administrador,                
        cuota_cobrada,
        comentario_validacion,
                    
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
        
        # 3 Validar que el cobro es del condominio del administrador        

        if cuota_cobrada.condominio != condominio:
            raise ValidationError(
                'La cuota cobrada que se quiere validar no es del condominio.'
            )

        # 4.1 Obtener la cuota cobrada con bloqueo de fila.
        cuota_cobrada = CuotaCobrada.objects.select_for_update().get(
            pk=cuota_cobrada.pk
        )

        # 4 Validar que el cobro previamente no fue validado        
        
        if cuota_cobrada.esta_validada:
            raise ValidationError(
                'La cuota cobrada ya previamente fue validada'
            )
                        
        # 5. Actualizar la cuota cobrada con los datos del administrador            

        cuota_cobrada.quien_valido=administrador
        cuota_cobrada.cuando_valido=timezone.now()
        cuota_cobrada.esta_validada=True
        cuota_cobrada.comentario_validacion=comentario_validacion
        cuota_cobrada.usuario_modifico=administrador

        cuota_cobrada.save(update_fields=['quien_valido', 'cuando_valido', 'esta_validada', 'comentario_validacion'
                        , 'usuario_modifico', 'fecha_modificacion' ])


        return {
            "comentario": cuota_cobrada.comentario_validacion            
                    
        }


