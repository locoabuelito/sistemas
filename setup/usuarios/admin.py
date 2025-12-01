# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Sector, UsuarioTecnico
from django.utils.translation import gettext_lazy as _

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['id_sector_tecnico', 'nombre_sector', 'activo_sector']
    list_filter = ['activo_sector']
    search_fields = ['nombre_sector']
    list_editable = ['activo_sector']

@admin.register(UsuarioTecnico)
class UsuarioTecnicoAdmin(UserAdmin):
    list_display = ['correo_tecnico', 'nombre_tecnico', 'sector_info', 'activo_tecnico', 'is_staff', 'fecha_creacion']
    list_filter = ['id_sector_tecnico', 'activo_tecnico', 'is_staff', 'is_superuser']
    search_fields = ['nombre_tecnico', 'correo_tecnico']
    ordering = ['nombre_tecnico']
    list_editable = ['activo_tecnico', 'is_staff']
    
    fieldsets = (
        (None, {'fields': ('correo_tecnico', 'password')}),
        (_('Información Personal'), {
            'fields': ('nombre_tecnico', 'id_sector_tecnico')
        }),
        (_('Permisos'), {
            'fields': ('activo_tecnico', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {
            'fields': ('last_login', 'fecha_creacion')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo_tecnico', 'nombre_tecnico', 'id_sector_tecnico', 'password1', 'password2', 'activo_tecnico', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'last_login']
    
    def sector_info(self, obj):
        return obj.id_sector_tecnico.nombre_sector if obj.id_sector_tecnico else "Sin sector"
    sector_info.short_description = 'Sector'