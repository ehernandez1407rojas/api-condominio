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
            comentario_validacion=comentario_validacion

        )

    
        # 10. Determinar estado de exigibilidad
        if cuota_cobrada.saldo <= 0:
            cuota_exigible.estado = 'P'
            cuota_exigible.save(update_fields=['estado'])

        return {
            "propiedad": propiedad.nombre,
            "importe_cobrado": importe_cobrado
                    
        }