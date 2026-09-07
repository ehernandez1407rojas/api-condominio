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
        cuota.save(
            update_fields=[
                'activo',
                'aplica_hasta',
                'comentario_cancelacion'
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
            estado='C'
        )
               

        return {
            "nombre": cuota.nombre,
            "tipo_cuota": cuota.tipo_cuota.clave,
            "cuotas_exigibles_canceladas": cuotas_exigibles_canceladas 
           
        }