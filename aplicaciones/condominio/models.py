from django.db import models
from django.contrib.auth.models import User
import os

from .api.managers import *
from django.conf import settings


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
    fecha_modificacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    class Meta:
        abstract = True
        
# --- Modelo Abstracto (para los catalogos estaticos) ---
class CatalogoBase(CreoModificoAbstract):
    clave = models.CharField(max_length=50)  # Ej: "ordinaria", "mensual"
    descripcion = models.CharField(max_length=100)  # Ej: "Cuota ordinaria", "Pago mensual"
    orden = models.DecimalField(max_digits=5, decimal_places=2)  # Para ordenar en listas
    
    class Meta:
        abstract = True  # ¡No crea tabla en la BD!

class TipoEstadoCondominio(CatalogoBase):
    class Meta:
        verbose_name = "Tipo Estado Condominio"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  
        

class Condominio(CreoModificoAbstract):
    nombre = models.CharField(max_length=50, unique=True,help_text="Máximo 50 caracteres" )
    nombre_corto = models.CharField(max_length=20, unique=True, default="", help_text="Máximo 20 caracteres")
    direccion = models.CharField(max_length=100, unique=True)
    inicio_servicio = models.DateField(blank=False, null=False)     
    estado_condominio =  models.ForeignKey(TipoEstadoCondominio, on_delete=models.PROTECT, default=1)  
    
    objects = CondominioManager()    
    
    class Meta:
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'      
        
    def __str__(self):
        return f'{self.nombre} {self.direccion}'     
        

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
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)
    quien_autoriza = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:        
        verbose_name = 'Tipo Gasto'
        verbose_name_plural = 'Tipos de Gastos' 
        
    def __str__(self):
        return f'{self.condominio.nombre} {self.clave}'  
        
class TipoRol(CatalogoBase):
    class Meta:
        verbose_name = "Tipo Rol"
        
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  
        
class TipoPeriodoCuota(CatalogoBase):
    class Meta:
        verbose_name = "Tipo Periodo de Cuota"
    
    def __str__(self):
        return f'{self.clave} {self.descripcion}'  

# ---tabla Usuario----

class Usuario(AbstractUser, CreoModificoAbstract):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('PROPIETARIO', 'Propietario'),
        ('CONSERJE', 'Conserje'),
    ]
    
    # Eliminamos campos que no usaremos del AbstractUser
    username = None
    first_name = None
    last_name = None
    email = None
    
    # Nuestros campos personalizados
    email_whatsapp = models.CharField(
        'correo o whatsapp',
        max_length=50,
        unique=True,
        help_text='Ingrese su correo electrónico o número de WhatsApp (solo números)'
    )
    nombre_completo = models.CharField('nombre completo', max_length=150)
    
    # Campos específicos
    tipo_usuario = models.CharField(
        'tipo de usuario',
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='PROPIETARIO'
    )
    
    esta_activo = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField(null=True, blank=True, default=False)
    
    # Propiedad (solo para propietarios)
    casa_departamento = models.ForeignKey(
        'CasaDepartamento', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='casa_departamento',
        verbose_name='casa departamento asignado'
    )
    # Para relacionarlo con el condominio
    condominio = models.ForeignKey( Condominio, on_delete=models.PROTECT,
        related_name='usuarios',  blank=True, null=True,
        verbose_name='condominio al que pertenece' )       
    
    USERNAME_FIELD = 'email_whatsapp'
    REQUIRED_FIELDS = ['nombre_completo']
    
    objects = UsuarioManager()
    
    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f'{self.nombre_completo} ({self.get_tipo_usuario_display()})'
    
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
        
        
# --- tablas transaccionales ---        
        
class Cuota(CreoModificoAbstract):
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)
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
        
class CasaDepartamento(CreoModificoAbstract):
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)   
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    titular = models.CharField(max_length=50)
    celular = models.CharField(max_length=30, unique=True)
    correo = models.EmailField(max_length=30, unique=True, default='')
    rol = models.ForeignKey(TipoRol, on_delete=models.PROTECT)
    
    objects = CasaDepartamentoManager()               
    
    class Meta:
        verbose_name = 'Casa Departamento'
        verbose_name_plural = 'Casas Departamentos' 
    def __str__(self):
        return f'{self.nombre} {self.direccion} {self.titular}' 
        
class CuotaCobrada(CreoModificoAbstract):
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)   
    casa_departamento = models.ForeignKey(CasaDepartamento, on_delete=models.PROTECT)
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
        return f'{self.id}  {self.casa_departamento} {self.periodo_cuota} {self.fecha} {self.importe_cobrado}'         
                
class Proveedor(CreoModificoAbstract):
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)   
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
                        
class GastoPagado(CreoModificoAbstract):
    condominio = models.ForeignKey(Condominio, on_delete=models.PROTECT)   
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