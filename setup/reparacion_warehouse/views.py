from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import (
    EquiposWarehouse, 
    Ubicacion, 
    TipoProblema, 
    AsignacionUbicacionWarehouse, 
    UbicacionWarehouse
)

@login_required
def reparacion_warehouse_view(request):
    usuario = request.user
    
    # Lógica para mostrar Warehouses según permisos
    if usuario.is_superuser:
        warehouses = Ubicacion.objects.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    else:
        # Asumiendo que existe la relación 'ubicaciones' en el modelo de usuario
        warehouses = usuario.ubicaciones.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    
    tipos_problema = TipoProblema.objects.filter(problema_activo=True).order_by('id_tipo_problema')
    
    context = {
        'warehouses': warehouses,
        'tipos_problema': tipos_problema,
        'usuario_logueado': request.user,
    }
    
    return render(request, 'reparacion_warehouse/reparacion_warehouse.html', context)

# --- API 1: OBTENER RACKS ---
@login_required
def obtener_racks_por_warehouse(request):
    warehouse_id = request.GET.get('warehouse_id')
    
    if not warehouse_id:
        return JsonResponse({'racks': []})
    
    try:
        racks = UbicacionWarehouse.objects.filter(
            id_ubicacion_id=warehouse_id,
            activo_ubicacion_warehouse=True
        ).values_list('rack', flat=True).distinct().order_by('rack')
        
        return JsonResponse({'racks': list(racks)})
        
    except Exception as e:
        print(f"Error al obtener racks: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# --- API 2: OBTENER EQUIPOS (Con Ficha Técnica) ---
@login_required
def obtener_equipos_por_warehouse(request):
    warehouse_id = request.GET.get('warehouse_id')
    rack_seleccionado = request.GET.get('rack')
    
    # --- DEBUGGING (Maldita sea, ¿por qué está vacío?) ---
    print(f"🔍 DEBUG REQUEST - Warehouse: '{warehouse_id}' | Rack: '{rack_seleccionado}'")
    
    if not warehouse_id:
        return JsonResponse({'equipos': []})
    
    try:
        filtros = {
            'activo_asignacion_equipo_ubicacion': True,
            'id_ubicacion_warehouse__id_ubicacion_id': warehouse_id,
            'id_ubicacion_warehouse__activo_ubicacion_warehouse': True
        }
        # Primero contamos cuántos hay SIN filtro de rack
        total_sin_rack = AsignacionUbicacionWarehouse.objects.filter(**filtros).count()
        print(f"📊 Equipos en Warehouse (Total): {total_sin_rack}")
        if rack_seleccionado:
            filtros['id_ubicacion_warehouse__rack'] = rack_seleccionado
            
        asignaciones = AsignacionUbicacionWarehouse.objects.filter(**filtros).select_related(
            'id_equipos_warehouse', 
            'id_ubicacion_warehouse'
        )
        print(f"📉 Equipos encontrados tras filtrar por Rack: {asignaciones.count()}")
        print(f"📝 Filtros aplicados: {filtros}")
        equipos_data = []
        for asignacion in asignaciones:
            equipo = asignacion.id_equipos_warehouse
            ubicacion_det = asignacion.id_ubicacion_warehouse
            
            equipos_data.append({
                'id': equipo.id_equipos_warehouse,
                'modelo': equipo.modelo_equipos_warehouse,
                'serial': equipo.serial_equipos_warehouse,
                # Detalle de ubicación para el select
                'ubicacion_detalle': f"Fila: {ubicacion_det.fila} - Col: {ubicacion_det.columna}",
                # Datos para la Ficha Técnica
                'ip': getattr(equipo, 'ip_equipos_warehouse', 'N/A'),
                'mac': getattr(equipo, 'mac_equipos_warehouse', 'N/A'),
                'firmware': getattr(equipo, 'firmware_equipos_warehouse', 'N/A')
            })
            
        return JsonResponse({'equipos': equipos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)