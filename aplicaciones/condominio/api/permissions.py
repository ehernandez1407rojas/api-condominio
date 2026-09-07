# permissions.py
from rest_framework import permissions

class IsAdminOnly(permissions.BasePermission):
    """Permiso para solo ADMINISTRADOR"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene rol ADMINISTRADOR
        usuario_rol = request.user.roles.filter(
            condominio=request.user.condominio,
            rol__clave='ADMINISTRADOR',
            activo=True
        ).exists()
        
        return usuario_rol


class IsAdminOrConserje(permissions.BasePermission):
    """Permiso para ADMINISTRADOR o CONSERJE"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene rol ADMINISTRADOR o CONSERJE
        usuario_rol = request.user.roles.filter(
            condominio=request.user.condominio,
            rol__clave__in=['ADMINISTRADOR', 'CONSERJE'],
            activo=True
        ).exists()
        
        return usuario_rol