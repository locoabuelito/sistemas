# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UsuarioTecnicoCreationForm, UsuarioTecnicoChangeForm
from .models import Sector, UsuarioTecnico, Ubicacion, UbicacionSector
from django.utils.translation import gettext_lazy as _


class SectorAdmin(admin.ModelAdmin):
    list_display = ['id_sector_tecnico', 'nombre_sector', 'activo_sector']
    list_filter = ['activo_sector']
    search_fields = ['nombre_sector']
    list_editable = ['activo_sector']

# --- NUEVO: Configuración del Inline para Ubicaciones ---
class UbicacionSectorInline(admin.TabularInline):
    model = UbicacionSector
    extra = 1  # Muestra una línea vacía para agregar rápido
    can_delete = True
    verbose_name = "Ubicación Asignada"
    verbose_name_plural = "Ubicaciones Asignadas"
    # raw_id_fields = ('ubicacion',) # Descomenta esto si tienes miles de ubicaciones para que cargue más rápido

class UsuarioTecnicoAdmin(UserAdmin):
    # Asignar los formularios personalizados
    add_form = UsuarioTecnicoCreationForm
    form = UsuarioTecnicoChangeForm
    model = UsuarioTecnico
    
    # --- NUEVO: Aquí integramos el Inline ---
    inlines = [UbicacionSectorInline]
    
    # Mostramos la ubicación en la lista
    list_display = [
        'correo_tecnico', 
        'nombre_tecnico', 
        'sector_info', 
        'get_ubicaciones',  # Función personalizada
        'password',         # Campo directo (mostrará el hash)
        'activo_tecnico', 
        'is_staff', 
        'fecha_creacion'
    ]
    
    # Define qué campos de 'list_display' deben ser enlaces.
    # Si no se define, por defecto sólo el primero de 'list_display' lo será
    # Recomendación: Enlazar el correo o el nombre.
    list_display_links = ('correo_tecnico', 'nombre_tecnico')
    
    # Filtros laterales
    list_filter = ['id_sector_tecnico', 'activo_tecnico', 'ubicaciones'] # Agregamos filtro por ubicación
    # Campos de búsqueda
    search_fields = ['nombre_tecnico', 'correo_tecnico']
    ordering = ['nombre_tecnico']
    # list_editable = ['activo_tecnico', 'is_staff']
    
    # Función para obtener las ubicaciones como texto separado por comas
    def get_ubicaciones(self, obj):
        # Obtiene todas las ubicaciones asociadas al usuario
        ubicaciones = obj.ubicaciones.all()
        if ubicaciones:
            # Crea un string: "WH-1, WH-2, WH-3"
            return ", ".join([u.nombre_ubicacion for u in ubicaciones])
        return "-"
    
    get_ubicaciones.short_description = 'Ubicación' # Título de la columna
    
    # Configuración de los campos al EDITAR un usuario
    fieldsets = (
        (None, {'fields': ('correo_tecnico', 'password')}), # 'password' aquí muestra el link para cambiar contraseña
        (_('Información Personal'), {
            'fields': ('nombre_tecnico', 'id_sector_tecnico') # Agregado ubicacion
        }),
        (_('Permisos'), {
            'fields': ('activo_tecnico', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {
            'fields': ('last_login', 'fecha_creacion')
        }),
    )
    
    # Configuración de los campos al CREAR un usuario nuevo
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo_tecnico', 'nombre_tecnico', 'id_sector_tecnico', 'password1', 'password2', 'activo_tecnico', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'last_login']
    
    ## Método para mostrar el nombre del sector
    def sector_info(self, obj):
        return obj.id_sector_tecnico.nombre_sector if obj.id_sector_tecnico else "-"
    sector_info.short_description = 'Sector'
    
    # Método para mostrar ubicación bonita en la lista
    def ubicacion_info(self, obj):
        # Accedemos a la relación. Si obj.ubicacion es None, devuelve "-"
        return obj.ubicacion.nombre_ubicacion if obj.ubicacion else "-"
    ubicacion_info.short_description = 'Ubicación'
    
# Registrar los modelos en el sitio de administración
admin.site.register(UsuarioTecnico, UsuarioTecnicoAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Ubicacion)