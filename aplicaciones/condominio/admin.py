from django.contrib import admin

from .models import *

# Register your models here.

# admin.site.register(TipoGasto)    
# admin.site.register(TipoCuota)
# admin.site.register(TipoFrecuencia)
# admin.site.register(TipoPeriodoCuota)
# admin.site.register(TipoRol)
# admin.site.register(TipoEstadoCondominio)

# admin.site.register(Cuota)
# admin.site.register(Propiedad)
# admin.site.register(CuotaCobrada)
# admin.site.register(GastoPagado)


## mas personalizacion 
## admin.site.register(Proveedor)
## admin.site.register(Condominio)




class BaseAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        basic_fields = [
            field.name for field in self.model._meta.fields
            if not field.is_relation or field.many_to_one
        ]
        
        # Agregamos métodos para relaciones especiales
        if hasattr(self.model, 'condominio'):
            basic_fields.append('get_condominio')
        
        return basic_fields
    
    @admin.display(description='Condominio')
    def get_condominio(self, obj):
        return str(obj.condominio) if obj.condominio else '-'
    

# --- las tablas que vemos en el admin   

@admin.register(Usuario)
class UsuarioAdmin(BaseAdmin):
    def get_list_display(self, request):
        # Obtenemos los campos base del padre
        base_fields = super().get_list_display(request)
        # Agregamos campos adicionales específicos para Usuario
        return base_fields 
    
    # list_filter = (  'esta_activo')
    search_fields = ('email_whatsapp', 'nombre_completo')
    
    
    fieldsets = (
        (None, {'fields': ('email_whatsapp', 'nombre_completo')}),
        ('Permisos', {'fields': ('esta_activo', 'is_staff')}),
        
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_creo = request.user
        else:
            obj.usuario_modifico = request.user
        super().save_model(request, obj, form, change)
        
    


@admin.register(Condominio)
class CondominioAdmin(BaseAdmin):
    pass



@admin.register(Propiedad)
class PropiedadAdmin(BaseAdmin):
    pass


@admin.register(TipoGasto)
class TipoGastoAdmin(BaseAdmin):
    pass

@admin.register(TipoCuota)
class TipoCuotaAdmin(BaseAdmin):
    pass



@admin.register(Rol)
class RolAdmin(BaseAdmin):
    pass

@admin.register(EstadoCondominio)
class TipoEstadoCondominioAdmin(BaseAdmin):
    pass

@admin.register(TipoToken)
class TipoTokenAdmin(BaseAdmin):
    pass

@admin.register(TokenUsuario)
class TokenUsuarioAdmin(BaseAdmin):
    pass

@admin.register(Cuota)
class CuotaAdmin(BaseAdmin):
    pass

@admin.register(CuotaExigible)
class CuotaAdmin(BaseAdmin):
    pass


@admin.register(CuotaCobrada)
class CuotaCobradaAdmin(BaseAdmin):
    pass



""" 
@admin.register(Proveedor)
class ProveedorAdmin(BaseAdmin):
    pass

@admin.register(GastoPagado)
class GastoPagadoAdmin(BaseAdmin):
    pass """