from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

from ..models import *

class UsuarioManager(BaseUserManager):
    def create_user(self, email_whatsapp, nombre_completo, password=None, **extra_fields):
        if not email_whatsapp:
            raise ValueError('El campo email/whatsapp es obligatorio')
        
        user = self.model(
            email_whatsapp=self.normalize_email_whatsapp(email_whatsapp),
            nombre_completo=nombre_completo,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_whatsapp, nombre_completo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email_whatsapp, nombre_completo, password, **extra_fields)

    @staticmethod
    def normalize_email_whatsapp(email_whatsapp):
        """
        Normaliza el campo email/whatsapp:
        - Para emails: convierte a minúsculas
        - Para WhatsApp: elimina espacios y caracteres especiales, dejando solo números
        """
        if '@' in email_whatsapp:
            return email_whatsapp.lower()
        # Limpia número de WhatsApp (elimina espacios, +, -, etc.)
        return re.sub(r'[^0-9]', '', email_whatsapp)
    

class CondominioManager(models.Manager):
    
    def listar_condominios_nombre(self, nombre):
        ## return self.filter(nombre_corto__icontains=nombre)
        ## return self.filter(nombre_corto=nombre)
        return self.filter(nombre_corto__icontains=nombre)
    
    def listar_condominios_por_nombre(self, nombre):
        ## return self.filter(nombre_corto__icontains=nombre)
        ## return self.filter(nombre_corto=nombre)
        return self.filter(nombre_corto__icontains=nombre)
                            
    def condominio_por_folio(self, folio):
        return self.filter(id = folio)
    
class CasaDepartamentoManager(models.Manager):
    def lista_casas_departamentos_posteriores(self, anio):
        return self.filter(
            fecha_creacion__year__gt=anio
        )
             
    def casas_departamentos_por_titular(self, titular):
        return self.filter(
            titular__icontains=titular
        ).order_by('titular')
    
    def casas_departamentos_por_titular_y_condominio(self, titular, condominio):
        return self.filter(
            titular__icontains=titular,
            condominio=condominio
        ).order_by('titular')
                            
                            