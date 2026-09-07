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
                    )
                )

        # Insertar todas las exigibilidades en una transaccion
        
        CuotaExigible.objects.bulk_create(cuotas_exigibles)
        

        return {
            "nombre": cuota.nombre,
            "tipo_cuota": tipo_cuota.clave,
            "cuotas_exigibles": len(cuotas_exigibles)           
        }