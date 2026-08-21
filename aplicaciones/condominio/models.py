from django.db import models
from django.contrib.auth.models import User
import os

## from .api.managers import *
from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
    

# Create your models here.
# --- Modelo Abstracto (para la auditoria de creacion y modificacion) ---
class CreoModificoAbstract(models.Model):    
    usuario_creo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_creado', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_modifico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_modificado', blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    class Meta:
        abstract = True

class AplicaDesdeHastaAbstract(models.Model):    
    aplica_desde = models.DateField(blank=False, null=False, help_text="Fecha inicial de vigencia de la tabla correspondiente")
    aplica_hasta = models.DateField(blank=True, null=True, help_text="Fecha final de vigencia de la tabla correspondiente")
    
    class Meta:
        abstract = True        
        
class EstadoCondominio(models.Model):
    clave = models.CharField(max_length=50)  # Ej: "ACTIVO", "SUSPENDIDO", "CANCELADO"
    descripcion = models.CharField(max_length=100)  # Ej: "ACTIVO", "SUSPENDIDO", "CANCELADO"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas
    class Meta:
        verbose_name = "Estado Condominio"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  

class Rol(models.Model):
    clave = models.CharField(max_length=50, unique=True)  # Ej: "ADMINISTRADOR", "PROPIETARIO", "CONSERJE"
    descripcion = models.CharField(max_length=100)  # Ej: "ADMINISTRADOR represenatnte del condominio", "PROPIETARIO dueño de la casa  o departamento", "CONCERJE"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas    

    class Meta:
        verbose_name = "Rol"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  
        
# Modelo con el objeto de la aplicacion
class Condominio(CreoModificoAbstract):
    nombre = models.CharField(max_length=50, unique=True,help_text="Máximo 50 caracteres" )
    nombre_corto = models.CharField(max_length=20, unique=True, default="", help_text="Máximo 20 caracteres")
    direccion = models.CharField(max_length=100, unique=True)
    inicio_servicio = models.DateField(blank=False, null=False)     
    estado_condominio =  models.ForeignKey(EstadoCondominio, on_delete=models.PROTECT, default=1)      
    
    objects = CondominioManager()    
    
    class Meta:
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'      
        
    def __str__(self):
        return f'{self.nombre} {self.direccion}'    

# --- Modelo Abstracto (para la auditoria de creacion y modificacion agregando el Condominio) ---
class CreoModificoCondominioAbstract(CreoModificoAbstract):    
    condominio =  models.ForeignKey(Condominio, on_delete=models.PROTECT)
    
    class Meta:
        abstract = True     
        
# --- Modelo Abstracto (para los catalogos estaticos) ---
class CatalogoBase(CreoModificoCondominioAbstract):    
    clave = models.CharField(max_length=50)  # Ej: "ordinaria", "mensual"
    descripcion = models.CharField(max_length=100)  # Ej: "Cuota ordinaria", "Pago mensual"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas
    
    class Meta:
        abstract = True  # ¡No crea tabla en la BD!

# --- Catálogos Concretos (Heredan de CatalogoBase) ---
class TipoCuota(CatalogoBase):
    class Meta:
        verbose_name = "Tipo de Cuota"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  
        
class TipoFrecuencia(CatalogoBase):
    class Meta:
        verbose_name = "Tipo Frecuencia de Pago"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  
        
class TipoGasto(CatalogoBase):    
    quien_autoriza = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:        
        verbose_name = 'Tipo Gasto'
        verbose_name_plural = 'Tipos de Gastos' 
        
    def __str__(self):
        return f'{self.condominio.nombre} {self.clave}'  
                
class TipoPeriodoCuota(CatalogoBase):
    class Meta:
        verbose_name = "Tipo Periodo de Cuota"
    
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  

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
        return f'{self.nombre_completo} )'
    
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
    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="roles"
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    fecha_fin = models.DateField(
        null=True, 
        blank=True, 
        help_text="Fecha en la que concluye la vigencia del rol (Null indica vigencia actual)"
    )
    activo = models.BooleanField(
        default=True, 
        help_text="Indica si el rol está vigente en la sesión actual"
    )

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
        
class Cuota(CreoModificoCondominioAbstract):
    
    nombre = models.CharField(max_length=30)
    tipo_cuota = models.ForeignKey(TipoCuota, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=30)
    importe = models.DecimalField(decimal_places=2, max_digits=12)
    frecuencia = models.ForeignKey(TipoFrecuencia, on_delete=models.PROTECT)
    aplica_desde = models.DateField(blank=False, null=False)
    aplica_hasta = models.DateField(blank=True, null=True)
        
    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas' 
        
    def __str__(self):
        return f'{self.condominio.nombre} {self.nombre}'       
        
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
    def __str__(self):
        return f'{self.nombre} {self.direccion} {self.propietario.nombre_completo}' 

# la relacioin del Usuario miembro con su propiedad casa o departamento
    
        
class CuotaCobrada(CreoModificoCondominioAbstract):    
    propiedad = models.ForeignKey(Propiedad, on_delete=models.PROTECT)
    importe_cobrado = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_cuota = models.ForeignKey(TipoCuota, on_delete=models.PROTECT)
    periodo_cuota = models.ForeignKey(TipoPeriodoCuota, on_delete=models.PROTECT)
    fecha = models.DateField(blank=False, null=False)
    comprobante = models.CharField(max_length=200)
    cuota_comprobante = models.ImageField(upload_to=ruta_comprobante_condominio, blank=True, null=True)
                   
    class Meta:
        verbose_name = 'Cuota Cobrada'
        verbose_name_plural = 'Cuotas Cobradas' 

    def __str__(self):
        return f'{self.id}  {self.propiedad} {self.periodo_cuota} {self.fecha} {self.importe_cobrado}'         
                
class Proveedor(CreoModificoCondominioAbstract):    
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    titular = models.CharField(max_length=50)
    celular = models.CharField(max_length=30, unique=True)
    correo = models.CharField(max_length=30, unique=True)
    comentarios = models.CharField(max_length=500)
    aplica_desde = models.DateField(blank=False, null=False)
    aplica_hasta = models.DateField(blank=True, null=True)
                   
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores' 
        
    def __str__(self):
        return f'{self.nombre} {self.direccion} '
                        
class GastoPagado(CreoModificoCondominioAbstract):    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    importe_pagado = models.DecimalField(max_digits=12, decimal_places=2)
    gasto = models.ForeignKey(TipoGasto, on_delete=models.PROTECT)    
    fecha = models.DateField(blank=False, null=False)
    comprobante = models.CharField(max_length=100)
    quien_autorizo = models.DateField(blank=True, null=True)
    cuando_autorizo = models.DateField(blank=True, null=True)
    gasto_comprobante = models.ImageField(upload_to=ruta_comprobante_condominio, blank=True, null=True)
                   
    class Meta:
        verbose_name = 'Gasto Pagado'
        verbose_name_plural = 'Gastos Pagados'   
        
    def __str__(self):
        return f'{self.id} {self.fecha} {self.proveedor} {self.gasto} {self.importe_pagado}'      

class Comite (CreoModificoCondominioAbstract, AplicaDesdeHastaAbstract):
    nombre = models.CharField(max_length=50, help_text="Nombre que identifica el comite")
    activo = models.BooleanField(
            default=True, 
            help_text="Indica si el rol está vigente en la sesión actual"
        ) 

class ComiteComposicion (CreoModificoCondominioAbstract):
    comite = models.ForeignKey(Comite, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    funcion_integrante = models.CharField(max_length=50, help_text="Indicacion del rol o funcion del miembro del comite")
    activo = models.BooleanField(
            default=True, 
            help_text="Indica si el ese miembro del comite esta activo o no"
    ) 

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