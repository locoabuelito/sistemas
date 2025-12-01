# reparacion_warehouse/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EquiposWarehouse, Ubicacion, TipoProblema

@login_required
def reparacion_warehouse_view(request):
    # Obtener todos los tipos de equipos únicos de la base de datos
    tipos_maquinas = EquiposWarehouse.objects.values_list(
        'tipo_equipos_warehouse', 
        flat=True
    ).distinct()
    
    # Obtener warehouses activos ordenados por ID
    warehouses = Ubicacion.objects.filter(activo_ubicacion=True).order_by('id_ubicacion')
    
    # Obtener tipos de problema activos desde la base de datos
    tipos_problema = TipoProblema.objects.filter(problema_activo=True).order_by('nombre_problema')
    
    context = {
        'tipos_maquinas': sorted(list(tipos_maquinas)),
        'warehouses': warehouses,
        'tipos_problema': tipos_problema,
        'usuario_logueado': request.user,
    }
    
    return render(request, 'reparacion_warehouse/reparacion_warehouse.html', context)