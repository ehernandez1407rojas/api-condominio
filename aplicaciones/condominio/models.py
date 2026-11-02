from django.db import models
from django.contrib.auth.models import User
import os
from django.db.models import Q

## from .api.managers import *
from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, MinValueValidator
from decimal import Decimal

from .api.managers import (
    CondominioManager,
    UsuarioManager,
    PropiedadManager,
)

# class CondominioManager(models.Manager):    
#     def listar_condominios_nombre(self, nombre):
#         return self.filter(nombre = nombre)
    
def ruta_comprobante_condominio(instance,  filename):
    nombre_condominio = instance.condominio.nombre_corto.replace(" ","_").lower()
    
    # Determinar el tipo de comprobante según la clase del modelo
    if instance.__class__.__name__ == 'GastoPagado':
        subcarpeta = 'pagos'  # Para gastos
    elif instance.__class__.__name__ == 'CuotaCobrada':
        subcarpeta = 'cobros'  # Para cuotas
    else:
        subcarpeta = 'otros'  # Por si hay otros tipos en el futuro
    
    return os.path.join('condominio_comprobates', nombre_condominio, subcarpeta, filename)
    

# --- Modelo Abstracto (para la auditoria de creacion y modificacion) ---
class CreoModificoAbstract(models.Model):    
    usuario_creo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_creado', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_modifico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_modificado', blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    class Meta:
        abstract = True

class AplicaDesdeHastaAbstract(models.Model):    
    aplica_desde = models.DateField(blank=False, null=False, help_text="Fecha inicial de vigencia de la tabla correspondiente")
    aplica_hasta = models.DateField(blank=True, null=True, help_text="Fecha final de vigencia de la tabla correspondiente")
    
    class Meta:
        abstract = True        
        
class EstadoCondominio(models.Model):
    clave = models.CharField(max_length=50, unique=True)  # Ej: "ACTIVO", "SUSPENDIDO", "CANCELADO"
    descripcion = models.CharField(max_length=100)  # Ej: "ACTIVO", "SUSPENDIDO", "CANCELADO"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas
    class Meta:
        verbose_name = "Estado Condominio"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  

class Rol(models.Model):
    clave = models.CharField(max_length=50, unique=True)  # Ej: "ADMINISTRADOR", "PROPIETARIO", "CONSERJE"
    descripcion = models.CharField(max_length=100)  # Ej: "ADMINISTRADOR representante del condominio", "PROPIETARIO dueño de la casa  o departamento", "CONCERJE"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas    
    class Meta:
        verbose_name = "Rol"
        
    def __str__(self):
        return f'{self.clave} '  
     
                
# ModeloS para atender  el objeto de la aplicacion
class Condominio(CreoModificoAbstract):
    nombre = models.CharField(max_length=50, unique=True,help_text="Máximo 50 caracteres" )
    nombre_corto = models.CharField(max_length=20, unique=True, default="", help_text="Máximo 20 caracteres")
    direccion = models.CharField(max_length=100, unique=True)
    inicio_servicio = models.DateField(blank=False, null=False)
    propiedad_cantidad = models.PositiveIntegerField(help_text="Número de propiedades en el condominio") ## NUEVO

    # Función para obtener el estado activo
    def get_estado_activo():
        from .models import EstadoCondominio
        # Esto lanzará EstadoCondominio.DoesNotExist si no existe
        return EstadoCondominio.objects.get(clave="ACTIVO").pk
         
    estado_condominio =  models.ForeignKey(EstadoCondominio, on_delete=models.PROTECT, default=get_estado_activo)      
    
    objects = CondominioManager()    
    
    class Meta:
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'      
        
    def __str__(self):
        return f'{self.nombre} {self.direccion}'    

# --- Modelo Abstracto (para la auditoria de creacion y modificacion agregando el Condominio) ---
class CreoModificoCondominioAbstract(CreoModificoAbstract):    
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.PROTECT        
    )
    
    class Meta:
        abstract = True     
        
# --- Modelo Abstracto (para los catalogos estaticos) ---
class CatalogoBase(CreoModificoCondominioAbstract):    
    clave = models.CharField(max_length=50, unique=True)  # Ej: "ordinaria", "mensual"
    descripcion = models.CharField(max_length=100)  # Ej: "Cuota ordinaria", "Pago mensual"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas
    
    class Meta:
        abstract = True  # ¡No crea tabla en la BD!

# --- Catálogos Concretos  
         
                   
# ---tabla Usuario----

class Usuario(AbstractUser, CreoModificoCondominioAbstract):    
    
    # Eliminamos campos que no usaremos del AbstractUser
    username = None
    first_name = None
    last_name = None
    email = None    

    # Sobrescribimos 'condominio' para permitir nulos
    condominio = models.ForeignKey(
        Condominio, 
        on_delete=models.PROTECT, 
        null=True,   # Permite NULL en la base de datos
        blank=True   # Permite vacío en formularios/admin/serializers
    )

    # Nuestros campos personalizados
    email_whatsapp = models.CharField(
        'correo o whatsapp',
        max_length=50,
        unique=True,
        help_text='Ingrese su correo electrónico o número de WhatsApp (solo números)'
    )
    nombre_completo = models.CharField('nombre completo', max_length=150)
    
    # Campos específicos    
    
    esta_activo = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField(null=True, blank=True, default=False)                 
           
    USERNAME_FIELD = 'email_whatsapp'
    REQUIRED_FIELDS = ['nombre_completo']
    
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f'{self.nombre_completo} ({self.email_whatsapp})'
    
    def clean(self):
        super().clean()
        # Validar que el campo email_whatsapp sea válido (email o número de teléfono)
        if '@' in self.email_whatsapp:
            try:
                validate_email(self.email_whatsapp)
            except ValidationError:
                raise ValidationError({'email_whatsapp': 'Ingrese un correo electrónico válido'})
        elif not self.email_whatsapp.isdigit():
            raise ValidationError({'email_whatsapp': 'Ingrese solo números para el WhatsApp'})
        elif len(self.email_whatsapp) < 10:
            raise ValidationError({'email_whatsapp': 'El número de WhatsApp debe tener al menos 10 dígitos'})
    
    def save(self, *args, **kwargs):
        # Normalizamos el campo email_whatsapp antes de guardar
        self.email_whatsapp = UsuarioManager.normalize_email_whatsapp(self.email_whatsapp)
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def es_email(self):
        """Determina si el identificador es un email"""
        return '@' in self.email_whatsapp
    
    @property
    def es_whatsapp(self):
        """Determina si el identificador es un número de WhatsApp"""
        return not self.es_email        


# la relacion usuario con los diferentes roles que puede tener por condominio
class UsuarioRol(CreoModificoAbstract):
    condominio = models.ForeignKey( Condominio, on_delete=models.PROTECT, related_name="usuarios" )
    usuario = models.ForeignKey( Usuario, on_delete=models.PROTECT, related_name="roles" )
    rol = models.ForeignKey( Rol, on_delete=models.PROTECT, related_name="usuarios" )
    fecha_fin = models.DateField( null=True, blank=True, help_text="Fecha en la que concluye la vigencia del rol (Null indica vigencia actual)" )
    activo = models.BooleanField( default=True, help_text="Indica si el rol está vigente en la sesión actual" )

    def clean(self):
        super().clean()
        # Validar que solo haya un ADMINISTRADOR activo
        if self.rol.clave == 'ADMINISTRADOR' and self.activo:
            qs = UsuarioRol.objects.filter(
                condominio=self.condominio,
                rol__clave='ADMINISTRADOR',
                activo=True
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            
            if qs.exists():
                raise ValidationError(
                    f"El condominio '{self.condominio.nombre}' ya tiene un administrador activo."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)        

    class Meta:
        verbose_name = "Usuario Rol"
        constraints = [            
            # Constraint: Evitar duplicados del mismo usuario con mismo rol activo en mismo condominio
            models.UniqueConstraint(
                fields=['usuario', 'condominio', 'rol'],
                condition=models.Q(activo=True),
                name='uq_usuario_condominio_rol_activo'
            )
        ]   

# --- tablas transaccionales ---                  
        
class Propiedad(CreoModificoCondominioAbstract):    
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    propietario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="propiedades"
        ) 
    
    objects = PropiedadManager()               
    
    class Meta:
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades' 
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'direccion'],                
                name='unique_direccion_propiedad_por_condominio'
            )
        ]
        
    def __str__(self):
        return f'{self.nombre} {self.direccion} {self.propietario.nombre_completo}' 

# la relacion del Usuario miembro con su propiedad casa o departamento
    
class TipoToken(models.Model):
    clave = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100)
    orden = models.DecimalField(max_digits=5, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(
        help_text="Duración del token en minutos"
    )

    class Meta:
        verbose_name = "Tipo Token"

    def __str__(self):
        return f"{self.clave} {self.descripcion}"

class TokenUsuario(CreoModificoCondominioAbstract):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoToken, on_delete=models.PROTECT)
    token_hash = models.CharField( max_length=64, help_text="Hash SHA-256 del token temporal"    )
    fecha_generacion = models.DateTimeField( help_text="Fecha en la que se generó el token temporal para el usuario"    )
    fecha_expiracion = models.DateTimeField( help_text="Fecha en la que expira el token temporal para el usuario"    )
    fecha_uso = models.DateTimeField( blank=True, null=True, help_text="Fecha y hora en la que se usó el token temporal"    )
    fecha_cancelacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora en la que se canceló el token temporal"
    )

    class Meta:
        verbose_name = "Token Usuario"

# para el area de Cuotas
# catalogo general para todos los condominios

class FrecuenciaCuota(models.Model):    
    clave = models.CharField(max_length=50, unique=True, help_text=" solo pueden ser MENSUAL o UNICA")   
    descripcion = models.CharField(max_length=100, help_text=" descripcion para ser MENSUAL o UNICA")
    orden = models.DecimalField(max_digits=5, decimal_places=2, help_text=" Para ordenar en listas ")   
    unidad_tiempo = models.CharField(max_length=20 , help_text=" Para cobrar cada MES o en un DIA")    

    class Meta:
        verbose_name = "Frecuencia de Cuota"
        
    def __str__(self):
        return f'{self.clave} '  
    
class TipoCuota(models.Model):    
    clave = models.CharField(max_length=50, unique=True, help_text=" solo pueden ser ORDINARIA o EXTRAORDINARIA")  
    descripcion = models.CharField(max_length=100, help_text=" descripcion para ORDINARIA o EXTRAORDINARIA") 
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas    
    frecuencia_cuota = models.ForeignKey(FrecuenciaCuota, on_delete=models.PROTECT, help_text="Solo pueden ser mensual o unica y cobrarse cada mes o en un dia")
    

    class Meta:
        verbose_name = "Tipo Cuota"
        
    def __str__(self):
        return f'{self.clave} '    

class EstadoCuotaExigible(models.TextChoices):
    EXIGIBLE = 'E', 'Exigible'
    PAGADA = 'P', 'Pagada'
    CANCELADA = 'C', 'Cancelada'    
    
# tablas transaccionales

class Cuota(CreoModificoCondominioAbstract):        
    tipo_cuota = models.ForeignKey(TipoCuota, on_delete=models.PROTECT, help_text="Solo pueden ser ordinaria o extraordinaria")
    nombre = models.CharField(max_length=100, help_text="En un nombre que se le puede dar a esa cuota")
    importe = models.DecimalField(decimal_places=2, max_digits=12,  help_text="Se debe indicar un importe para cualquiera de las cuotas ")
    activo = models.BooleanField( default=True, help_text="Indica la cuota está activo o no" )
    aplica_desde = models.DateField(help_text="Fecha inicial de exigibilidad de la cuota puede se menor,  mayor o igual a la fecha del sistema")
    aplica_hasta = models.DateField( help_text="Fecha final de exigibilidad de la cuota, debe ser mayor a la fecha inicial y puede se menor,  mayor o igual a la fecha del sistema")
    comentario_cancelacion = models.CharField(max_length=100, blank=True, null=True, help_text="Comentario con el motivo de la cancelacion")
    recargo_mes_dia = models.IntegerField(blank=True, null=True, help_text="Día del mes apartir del cual se pagara recargo")
    importe_regarco_mes = models.IntegerField(blank=True, null=True, help_text="Importe del recargo si paga dentro del mes")
    importe_recargo_mes_siguiente = models.IntegerField(blank=True, null=True, help_text="Importe del recargo por cada mes de atraso si paga después del mes")
       
    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas' 
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'tipo_cuota'],
                condition=Q(activo=True),
                name='unique_cuota_activa_por_condominio_y_tipo'
            )
        ]
        
    def __str__(self):
        return f'{self.condominio.nombre} {self.nombre}'    


class CuotaExigible (CreoModificoCondominioAbstract):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.PROTECT, help_text="Propiedad que debe  pagar la cuota")
    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, help_text="El nombre de la cuota que lleva las condiciones de la cuota")
    fecha_exigibilidad = models.DateField(help_text="Fecha en la que sera exigible la cuota y se debera de pagar en caso de mensual sera al inicio de mes")
    importe_cuota = models.DecimalField(max_digits=12, decimal_places=2, help_text="Importe a pagar de la cuota")
    estado = models.CharField( max_length=1, choices=EstadoCuotaExigible.choices, default=EstadoCuotaExigible.EXIGIBLE, help_text="Estado de la exigibilidad de la cuota")


#         
class CuotaCobrada(CreoModificoCondominioAbstract):    
    propiedad = models.ForeignKey(Propiedad, on_delete=models.PROTECT, help_text="Propiedad que paga la cuota")
    cuota_exigible = models.ForeignKey(CuotaExigible, on_delete=models.PROTECT, help_text="Cuota que se paga")
    importe_exigible = models.DecimalField(max_digits=12, decimal_places=2, help_text="Importe exigible de la cuota")   
    importe_cobrado = models.DecimalField(max_digits=12, decimal_places=2, help_text="Importe cobrado de esa cuota")    
    quien_recibe = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='%(class)s_recibio', help_text="La persona que recibe la cuota")    
    fecha_recepcion = models.DateTimeField(auto_now_add=True, help_text="Sera la fecha y hora de cuando se recibe la cuota no se puede cambiar")
    comprobante = models.CharField(max_length=100, help_text="Es una captura libre de como se comprueba el importe")
    cuota_comprobante = models.FileField(upload_to=ruta_comprobante_condominio, blank=True, null=True, help_text="archivo en formato pdf o jpg solamente")
    quien_valido = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='%(class)s_valido', blank=True, null=True, help_text="Sera el administrador")    
    cuando_valido = models.DateTimeField(blank=True, null=True, help_text="Sera la fecha y hora cuando el administrador recibe y valida las cuotas")
    saldo = models.DecimalField(max_digits=12, decimal_places=2, help_text="Diferencia entre el monto de la cuota definido y lo pagado puede ser a favor o en contra se pasa al siguiente pago", default=0)
    esta_validada = models.BooleanField(default=False)
    comentario_validacion=models.CharField(max_length=100, blank=True, null=True, help_text="Comentario del administrador al validar el cobro")

    class Meta:
        verbose_name = 'Cuota Cobrada'
        verbose_name_plural = 'Cuotas Cobradas' 
        indexes = [
                models.Index(fields=['fecha_recepcion']),
            ]

    def __str__(self):
        return f'{self.id}  {self.propiedad}  {self.fecha_recepcion} {self.importe_cobrado}'         


# para el area de GASTOS

# Agregar con el CODOMINIO
class TipoGasto(CreoModificoCondominioAbstract):    
    clave = models.CharField(max_length=50,  help_text="Definición de los diferente conceptos o tipos de gastos por cada condominio" )  
    descripcion = models.CharField(max_length=100, help_text="Detalle adicional de los diferente conceptos o tipos de gastos" )  
    orden = models.DecimalField(max_digits=5, decimal_places=2, help_text="Para definir un orden de los conceptos")  
    
    class Meta:        
        verbose_name = 'Tipo Gasto'
        verbose_name_plural = 'Tipos de Gastos' 
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'clave'],                
                name='unique_clave_por_condominio_y_tipo_gasto'
            )
        ]
        
    def __str__(self):
        return f' {self.clave}'  

class SubTipoGasto(CreoModificoCondominioAbstract):    
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.PROTECT, help_text="Tipo gasto")
    clave = models.CharField(max_length=50, help_text="Definición del subtipo gasto, ejemplo nombre del empleado" )  
    descripcion = models.CharField(max_length=100, help_text="Detalle adicional de los  subtipos de gastos, es opcional este catalogo" )  
    orden = models.DecimalField(max_digits=5, decimal_places=2, help_text="Para definir un orden de los conceptos")  
    
    class Meta:        
        verbose_name = 'Sub Tipo Gasto'
        verbose_name_plural = 'Sub Tipos de Gastos' 
        constraints = [
                    models.UniqueConstraint(
                        fields=['condominio', 'tipo_gasto', 'clave'],                
                        name='unique_clave_por_condominio_y_subtipo_gasto'
                    )
                ]
        
    def __str__(self):
        return f' {self.clave}' 

class SituacionProveedor(models.Model):    
    clave = models.CharField(max_length=50, unique=True, help_text="Definición de los diferente estado que puede tener un proveedor")  # Ej: "RECOMENDABLE", "VETADO", "PENDIENTE"
    descripcion = models.CharField(max_length=100, help_text="Detalle adicional de los diferentes estado que puede tener un proveedor")  # Ej: "RECOMENDABLE", "VETADO", "PENDIENTE"
    orden = models.DecimalField(max_digits=5, decimal_places=2, help_text="Para definir un orden de los conceptos")  # Para ordenar en listas

    class Meta:
        verbose_name = "Situacion Proveedor"
        
    def __str__(self):
        return f'{self.clave} '  
                              

class Proveedor(CreoModificoCondominioAbstract, AplicaDesdeHastaAbstract):    
    nombre = models.CharField(max_length=50, help_text="Nombre del proveedor del bien o servicio")
    direccion = models.CharField(max_length=100, help_text="Direccion del proveedor del bien o servicio")    
    celular = models.CharField(max_length=30,  blank=True, null=True, help_text="Celular del proveedor del bien o servicio" )
    correo = models.EmailField(max_length=30,  blank=True, null=True, help_text="Correo electronico del proveedor del bien o servicio")     
    situacion =  models.ForeignKey(SituacionProveedor, on_delete=models.PROTECT) 
    
                   
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores' 
        constraints = [
            models.UniqueConstraint(
                fields=['condominio', 'celular'],                
                name='unique_proveedor_celular_por_condominio'
            ),
            models.UniqueConstraint(
                            fields=['condominio', 'correo'],                
                            name='unique_proveedor_correo_por_condominio'
                        ), 
        ]
        
    def __str__(self):
        return f'{self.nombre} {self.direccion} '

class ProveedorComentario(CreoModificoCondominioAbstract): 
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT) 
    comentario = models.CharField(max_length=200) 

    class Meta:
        verbose_name = 'Comentario Proveedor'

    def __str__(self):
            return f'{self.proveedor.nombre} {self.comentario} '

class GastoPagado(CreoModificoCondominioAbstract):    
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.PROTECT, help_text="Tipo de gasto")    
    sub_tipo_gasto = models.ForeignKey(SubTipoGasto, on_delete=models.PROTECT, blank=True, null=True, help_text="Con el subtipo de gasto se da mas detalle de a quien o a que corresponde")  
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, blank=True, null=True, help_text="Proveedor al que se le paga el bien o servicio ")
    importe_pagado = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], help_text="Importe pagado por los bienes o servicios")    
    descripcion = models.CharField(max_length=200, help_text="Detalle adicional del gasto efectuado")  
    fecha = models.DateField( help_text="Fecha del gasto en caso de comprobante el que se indique en dicho comprobante")
    gasto_comprobante = models.FileField(upload_to=ruta_comprobante_condominio, blank=True, null=True, help_text="ruta del archivo  en formato pdf o jpg del comprobante del  gasto")
    esta_autorizado = models.BooleanField(default=False, help_text="En un estado del gasto, si el administrador lo hizo queda como verdadero, si lo hace el conserje queda con el default")
    quien_autorizo = models.ForeignKey( Usuario, on_delete=models.PROTECT, related_name='gastos_autorizados', blank=True, null=True, help_text="Será el administrador" )
    cuando_autorizo = models.DateField(blank=True, null=True, help_text="Es la fecha de sistema en la que el administrador lo autorizo")
    esta_cancelado = models.BooleanField(default=False, help_text="Deben ser excepcional pero se le permitirá al adminstrador cancelar un gasto sin importar si previamente fue autorizado")
    quien_cancelo = models.ForeignKey( Usuario, on_delete=models.PROTECT, related_name='gastos_cancelados', blank=True, null=True, help_text="Será el administrador" )
    cuando_cancelo = models.DateField(blank=True, null=True, help_text="Es la fecha de sistema en la que el administrador lo cancela")
    motivo_cancelacion = models.CharField(max_length=100, blank=True, null=True, help_text="Información que justifique la cancelacion del gasto")  
                   
    class Meta:
        verbose_name = 'Gasto Pagado'
        verbose_name_plural = 'Gastos Pagados' 
        indexes = [
                models.Index(fields=['fecha']),
            ]
          
        
    def __str__(self):
        return f'{self.id} {self.fecha} {self.proveedor} {self.importe_pagado}'      


##
## Para la seccion Comité

class Comite (CreoModificoCondominioAbstract, AplicaDesdeHastaAbstract):
    nombre = models.CharField(max_length=50, help_text="Nombre que identifica el comite")
    descripcion = models.CharField(max_length=100, help_text="Descripcion adicional en la creación del comité ")
    activo = models.BooleanField(default=True,help_text="Indica si el Comité está vigente ")
    class Meta:
        verbose_name = "Comite" 
        constraints = [
            models.UniqueConstraint(
                    fields=['condominio'],
                    condition=Q(activo=True),
                    name='uq_condominio_comite_activo' )     
                ]
                       
    def __str__(self):
        return f'{self.nombre} {self.descripcion}'  

class ComiteIntegrante (CreoModificoCondominioAbstract, AplicaDesdeHastaAbstract):    
    comite = models.ForeignKey(Comite,  on_delete=models.PROTECT, help_text="Son los integrantes solo de este comite")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, help_text="Propietario usuario perteneciente al condominio")
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, help_text="Indicacion del rol o funcion del miembro del comite, de las opciones fijas a nivel sistema")    
    activo = models.BooleanField(default=True, help_text="Indica si el ese miembro del comite esta activo o no" )

    class Meta:
        verbose_name = "Integrantes Comité"   
        constraints = [
            # Un comité solo puede tener un administrador activo
            models.UniqueConstraint(
                fields=['comite'],
                condition=Q(activo=True, rol_id=1),
                name='uq_administrador_activo_por_comite'
            ),

            # Un integrante solo puede tener un rol activo dentro del comité
            models.UniqueConstraint(
                fields=['comite', 'usuario'],
                condition=Q(activo=True),
                name='uq_integrante_comite_usuario_activo'
            ),   
        ]    

class TransferenciaAdministracion(CreoModificoCondominioAbstract):
    administrador_anterior = models.ForeignKey( Usuario, on_delete=models.PROTECT, related_name="transferencias_administracion_anterior", help_text="Administrador anterior del condominio" )
    administrador_nuevo = models.ForeignKey( Usuario, on_delete=models.PROTECT, related_name="transferencias_administracion_nuevo", help_text="Nuevo administrador del condominio" )
    comite_inactivado = models.ForeignKey( Comite, on_delete=models.PROTECT, related_name="transferencias_administracion", help_text="Comité que se inactiva durante la transferencia" )
    fecha_transferencia = models.DateField( help_text="Fecha en que se realiza la transferencia de administración" )
    comentario = models.CharField( max_length=200,  help_text="Comentario relacionado con la transferencia de administración" )

    class Meta:
        verbose_name = "Transferencia Administración"   
       

""" 
    CONVOCADA 
    CELEBRADA 
    CANCELADA         

 """

class ConvocatoriaEstadoTipo(models.Model):
    clave = models.CharField(max_length=50, unique=True, help_text="Clave para identificar el tipo estado que tiene una  convocatoría")  
    descripcion = models.CharField(max_length=100, help_text="Descripcion adicional para la clave de la iformación que integra una del estado de una convocatoria, ejemplo CONVOCADA, CELEBRADA") 
    orden = models.DecimalField(max_digits=5, decimal_places=2, help_text="Permite indicar un orden en las lista de selección")    
    
    class Meta:
        verbose_name = "Tipo Estado Convocatoria"
        
    def __str__(self):
        return f'{self.clave}  {self.descripcion}'     

class AsambleaTipo(models.TextChoices):
    ORDINARIA = 'O', 'Ordinaria'
    EXTRAORDINARIA = 'E', 'Extraordinaria'

class Convocatoria (CreoModificoCondominioAbstract):
    comite = models.ForeignKey(Comite, on_delete=models.PROTECT,  help_text="Comité al que se asocia la convocatoria")
    asamblea = models.CharField( max_length=1, choices=AsambleaTipo.choices, help_text="Define el tipo de asamblea a la que se convoca")
    documento=models.FileField(upload_to=ruta_comprobante_condominio, blank=True, null=True, help_text="archivo en formato pdf solamente")
    nombre = models.CharField(max_length=50, help_text="Nombre que identifica la convocatoria")
    descripcion = models.CharField(max_length=100, help_text="Descripcion de la convocatoria motivo ")
    fecha = models.DateField(  help_text="Fecha a celebrar la asamblea motivo de la convocatoria, debe ser mayor a la fecha del sistema")
    estado_convocatoria = models.ForeignKey(ConvocatoriaEstadoTipo, on_delete=models.PROTECT, default=1 , help_text="Estado que tiene una convocatoria")
    class Meta:
        verbose_name = "Convocatoria"
        indexes = [
            models.Index(fields=['fecha']),
        ]
            
    def __str__(self):
            return f'{self.nombre} {self.descripcion}'    
                
    
class ActaAsamblea(CreoModificoCondominioAbstract):
    comite = models.ForeignKey(Comite, on_delete=models.PROTECT,  help_text="Comité al que se asocia el acta")
    convocatoria = models.ForeignKey(Convocatoria, on_delete=models.PROTECT, help_text="La convocatoria que da lugar a la presente acta")
    documento=models.FileField(upload_to=ruta_comprobante_condominio, blank=True, null=True, help_text="archivo en formato pdf solamente")
    fecha = models.DateField( help_text="Fecha en la que se celebró la asamblea, debe ser menor o igual a la fecha de sistema")
    
    class Meta:
        verbose_name = "Acta"
        indexes = [
            models.Index(fields=['fecha']),
        ]

        
### PARA STRIPE
####

""" 
class MensualidadEstado(models.TextChoices):
    PENDIENTE = 'P', 'Pendiente'
    COBRADA = 'C', 'Cobrada'    

class Mensualidad(CreoModificoCondominioAbstract):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.PROTECT, help_text="Propiedad que debe  pagar la cuota")
    mes_anio=models.DateField(help_text="Mes y año de la mensualidad")
    estado=models.CharField(max_length=1, choices=MensualidadEstado.choices, default=MensualidadEstado.PENDIENTE, help_text="Estado de la mensualidad ")


    tipo = models.ForeignKey(TipoToken, on_delete=models.PROTECT)
    token_hash = models.CharField( max_length=64, help_text="Hash SHA-256 del token temporal"    )
    fecha_generacion = models.DateTimeField( help_text="Fecha en la que se generó el token temporal para el usuario"    )
    fecha_expiracion = models.DateTimeField( help_text="Fecha en la que expira el token temporal para el usuario"    )
    fecha_uso = models.DateTimeField( blank=True, null=True, help_text="Fecha y hora en la que se usó el token temporal"    )                       

 """    