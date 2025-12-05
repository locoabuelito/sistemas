# reparacion_warehouse/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EquiposWarehouse, Ubicacion, TipoProblema

@login_required
def reparacion_warehouse_view(request):
    # 1. Obtener todos los tipos de equipos (sin cambios)
    tipos_maquinas = EquiposWarehouse.objects.values_list(
        'tipo_equipos_warehouse', 
        flat=True
    ).distinct()
    
    # 2. LÓGICA MODIFICADA: Filtrar Warehouses por Usuario
    usuario = request.user
    
    # Opcional: Si es superusuario (admin), le mostramos TODAS las ubicaciones.
    # Si es técnico normal, solo mostramos las asignadas en la tabla intermedia.
    if usuario.is_superuser:
        warehouses = Ubicacion.objects.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    else:
        # Accedemos a la relación 'ubicaciones' definida en tu modelo UsuarioTecnico
        warehouses = usuario.ubicaciones.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    
    # 3. Obtener tipos de problema activos desde la base de datos
    tipos_problema = TipoProblema.objects.filter(problema_activo=True).order_by('id_tipo_problema')
    
    context = {
        'tipos_maquinas': sorted(list(tipos_maquinas)),
        'warehouses': warehouses, # Ahora esta variable trae solo lo asignado
        'tipos_problema': tipos_problema,
        'usuario_logueado': request.user,
    }
    
    return render(request, 'reparacion_warehouse/reparacion_warehouse.html', context)