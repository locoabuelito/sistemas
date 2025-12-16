# reparacion_warehouse/views.py

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import F

# Importación de modelos
from .models import (
    EquiposWarehouse, 
    Ubicacion, 
    TipoProblema, 
    AsignacionUbicacionWarehouse, 
    UbicacionWarehouse,
    SolicitudReparacion
)

# ==============================================================================
# BLOQUE 1: VISTA DE RENDERIZADO (HTML)
# Carga la plantilla principal y los contextos iniciales.
# ==============================================================================

@login_required
def reparacion_warehouse_view(request):
    """
    Vista principal que renderiza el template HTML.
    Carga los Warehouses iniciales según permisos y los Tipos de Problema.
    """
    usuario = request.user
    
    # 1. Lógica de permisos para ver Warehouses
    if usuario.is_superuser:
        warehouses = Ubicacion.objects.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    else:
        # Asumiendo relación 'ubicaciones' en el modelo de usuario (ManyToMany o ForeignKey)
        warehouses = usuario.ubicaciones.filter(activo_ubicacion=True).order_by('nombre_ubicacion')
    
    # 2. Catálogo de problemas
    tipos_problema = TipoProblema.objects.filter(problema_activo=True).order_by('id_tipo_problema')
    
    context = {
        'warehouses': warehouses,
        'tipos_problema': tipos_problema,
        'usuario_logueado': request.user,
    }
    
    return render(request, 'reparacion_warehouse/reparacion_warehouse.html', context)


# ==============================================================================
# BLOQUE 2: APIS DE FILTROS (SELECTS EN CASCADA)
# Endpoints GET para obtener Racks y Equipos dinámicamente.
# ==============================================================================

@login_required
def obtener_racks_por_warehouse(request):
    """
    API: Devuelve lista de Racks únicos dado un Warehouse ID.
    """
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


@login_required
def obtener_equipos_por_warehouse(request):
    """
    API: Busca equipos disponibles filtrando por Warehouse y opcionalmente por Rack.
    Devuelve también datos técnicos (IP, MAC, Firmware) para la ficha.
    """
    warehouse_id = request.GET.get('warehouse_id')
    rack_seleccionado = request.GET.get('rack')
    
    # --- Debugging ---
    print(f"🔍 DEBUG REQUEST - Warehouse: '{warehouse_id}' | Rack: '{rack_seleccionado}'")
    
    if not warehouse_id:
        return JsonResponse({'equipos': []})
    
    try:
        filtros = {
            'activo_asignacion_equipo_ubicacion': True,
            'id_ubicacion_warehouse__id_ubicacion_id': warehouse_id,
            'id_ubicacion_warehouse__activo_ubicacion_warehouse': True
        }

        # Aplicar filtro de Rack si existe
        if rack_seleccionado:
            filtros['id_ubicacion_warehouse__rack'] = rack_seleccionado
            
        # Consulta optimizada con select_related para evitar N+1 queries
        asignaciones = AsignacionUbicacionWarehouse.objects.filter(**filtros).select_related(
            'id_equipos_warehouse', 
            'id_ubicacion_warehouse'
        )
        
        print(f"📉 Equipos encontrados: {asignaciones.count()}")
        
        equipos_data = []
        for asignacion in asignaciones:
            equipo = asignacion.id_equipos_warehouse
            ubicacion_det = asignacion.id_ubicacion_warehouse
            
            equipos_data.append({
                'id': equipo.id_equipos_warehouse,
                'modelo': equipo.modelo_equipos_warehouse,
                'serial': equipo.serial_equipos_warehouse,
                'fila': ubicacion_det.fila,
                'columna': ubicacion_det.columna,
                # Datos técnicos para autocompletar formulario
                'ip': getattr(equipo, 'ip_equipos_warehouse', 'N/A'),
                'mac': getattr(equipo, 'mac_equipos_warehouse', 'N/A'),
                'firmware': getattr(equipo, 'firmware_equipos_warehouse', 'N/A')
            })
            
        return JsonResponse({'equipos': equipos_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==============================================================================
# BLOQUE 3: APIS DE GESTIÓN (CRUD SOLICITUDES)
# Listar, Crear, Editar y "Eliminar" (Ocultar) solicitudes.
# ==============================================================================

@login_required
def listar_solicitudes(request):
    """
    API (READ): Lista todas las solicitudes activas.
    Incluye lógica compleja para determinar la ubicación actual del equipo.
    """
    try:
        # Filtramos solo las activas
        solicitudes = SolicitudReparacion.objects.filter(
            solicitud_activa=True
        ).select_related('equipo', 'tecnico', 'tipo_problema').order_by('-fecha_creacion')

        data = []
        for s in solicitudes:
            fecha_local = timezone.localtime(s.fecha_creacion)
            fecha_fmt = fecha_local.strftime('%d/%m/%Y %H:%M')
            
            # --- CORRECCIÓN AQUÍ ---
            # Nombre técnico seguro: Evitamos llamar a .username si no existe
            nombre_tec = "Técnico"
            if s.tecnico:
                # 1. Intentamos obtener 'nombre_tecnico'
                nombre_tec = getattr(s.tecnico, 'nombre_tecnico', None)
                # 2. Si no existe o está vacío, intentamos 'nombre'
                if not nombre_tec:
                    nombre_tec = getattr(s.tecnico, 'nombre', None)
                # 3. Si sigue sin existir, usamos la representación string del objeto (lo más seguro)
                if not nombre_tec:
                    nombre_tec = str(s.tecnico)

            # Ubicación segura
            ubicacion_str = "Bodega / Tránsito"
            try:
                asignacion = AsignacionUbicacionWarehouse.objects.filter(
                    id_equipos_warehouse=s.equipo,
                    activo_asignacion_equipo_ubicacion=True
                ).select_related('id_ubicacion_warehouse__id_ubicacion').first()

                if asignacion and asignacion.id_ubicacion_warehouse:
                    wh_obj = asignacion.id_ubicacion_warehouse
                    nombre_wh = wh_obj.id_ubicacion.nombre_ubicacion
                    ubicacion_str = f"{nombre_wh} ➝ Rack {wh_obj.rack} ➝ F:{wh_obj.fila}/C:{wh_obj.columna}"
            except Exception as e:
                print(f"Error ubicacion id {s.id_solicitud}: {e}")

            data.append({
                'id_solicitud': s.id_solicitud,
                'equipo_modelo': s.equipo.modelo_equipos_warehouse if s.equipo else "Sin Equipo",
                'equipo_serial': s.equipo.serial_equipos_warehouse if s.equipo else "S/N",
                'tecnico_nombre': nombre_tec,
                'tipo_problema': s.tipo_problema.nombre_problema if s.tipo_problema else "General",
                'th_cantidad': s.th_cantidad,
                'descripcion': s.descripcion,
                'estado': s.estado,
                'fecha_creacion': fecha_fmt,
                'ubicacion_completa': ubicacion_str
            })
            
        return JsonResponse({'solicitudes': data})
    except Exception as e:
        print(f"Error CRITICO al listar: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def crear_solicitud(request):
    """
    API (CREATE): Recibe JSON y crea un nuevo registro en SolicitudReparacion.
    """
    try:
        data = json.loads(request.body)
        
        nueva_solicitud = SolicitudReparacion(
            equipo_id = data.get('equipo_id'),
            tecnico = request.user,
            tipo_problema_id = data.get('tipo_problema_id'),
            th_cantidad = data.get('th_cantidad'),
            descripcion = data.get('descripcion'),
            estado = 'pendiente',
            solicitud_activa = True
        )
        nueva_solicitud.save()
        
        return JsonResponse({'status': 'success', 'message': 'Solicitud guardada correctamente'})
    except Exception as e:
        print(f"Error al crear solicitud: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def editar_solicitud(request):
    """
    API (UPDATE): Actualiza campos específicos de una solicitud existente.
    """
    try:
        data = json.loads(request.body)
        id_solicitud = data.get('id_solicitud')
        
        solicitud = get_object_or_404(SolicitudReparacion, pk=id_solicitud)
        
        # Actualizamos campos editables
        solicitud.tipo_problema_id = data.get('tipo_problema_id')
        solicitud.th_cantidad = data.get('th_cantidad')
        solicitud.descripcion = data.get('descripcion')
        
        solicitud.save()
        
        return JsonResponse({'status': 'success', 'message': 'Solicitud actualizada correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def ocultar_solicitud(request, id_solicitud):
    """
    API (DELETE - SOFT): Marca la solicitud como inactiva en lugar de borrarla de la BD.
    """
    try:
        solicitud = get_object_or_404(SolicitudReparacion, pk=id_solicitud)
        
        solicitud.solicitud_activa = False
        solicitud.save()
        
        return JsonResponse({'status': 'success', 'message': 'Solicitud eliminada de la vista'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
@require_POST
def recepcionar_equipo(request):
    try:
        data = json.loads(request.body)
        id_solicitud = data.get('id_solicitud')
        id_ubicacion_warehouse_destino = data.get('id_ubicacion_warehouse') # ID específico (fila/columna)
        notas_cierre = data.get('notas', '')

        if not id_solicitud or not id_ubicacion_warehouse_destino:
            return JsonResponse({'status': 'error', 'message': 'Faltan datos (Solicitud o Ubicación)'}, status=400)

        # 1. Obtener la solicitud
        solicitud = get_object_or_404(SolicitudReparacion, pk=id_solicitud)
        
        # 2. Verificar que no esté ya cerrada
        if solicitud.estado == 'completado':
            return JsonResponse({'status': 'error', 'message': 'Esta solicitud ya fue cerrada'}, status=400)

        # 3. LÓGICA DE MOVIMIENTO DE INVENTARIO
        # a) Desactivar la asignación actual (donde estaba antes o "en tránsito")
        AsignacionUbicacionWarehouse.objects.filter(
            id_equipos_warehouse=solicitud.equipo,
            activo_asignacion_equipo_ubicacion=True
        ).update(
            activo_asignacion_equipo_ubicacion=False,
            fecha_desasignacion=timezone.now()
        )

        # b) Crear nueva asignación en la ubicación seleccionada
        nueva_asignacion = AsignacionUbicacionWarehouse(
            id_equipos_warehouse=solicitud.equipo,
            id_ubicacion_warehouse_id=id_ubicacion_warehouse_destino,
            observaciones=f"Reingreso por reparación #{id_solicitud}. {notas_cierre}",
            activo_asignacion_equipo_ubicacion=True
        )
        nueva_asignacion.save()

        # 4. Actualizar la Solicitud
        solicitud.estado = 'completado'
        # Podrías agregar un campo fecha_cierre en tu modelo si quisieras
        solicitud.descripcion += f"\n[CIERRE] {timezone.now().strftime('%d/%m/%Y')}: {notas_cierre}" 
        solicitud.save()

        return JsonResponse({'status': 'success', 'message': 'Equipo recepcionado y reubicado correctamente'})

    except Exception as e:
        print(f"Error Recepción: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def obtener_posiciones_rack(request):
    warehouse_id = request.GET.get('warehouse_id')
    rack = request.GET.get('rack')
    
    try:
        # Buscamos las ubicaciones físicas (celdas) de ese rack
        ubicaciones = UbicacionWarehouse.objects.filter(
            id_ubicacion_id=warehouse_id,
            rack=rack,
            activo_ubicacion_warehouse=True
        ).order_by('fila', 'columna')
        
        data = []
        for u in ubicaciones:
            # Opcional: Verificar si está ocupada
            ocupada = AsignacionUbicacionWarehouse.objects.filter(
                id_ubicacion_warehouse=u,
                activo_asignacion_equipo_ubicacion=True
            ).exists()
            
            estado_str = "(Ocupada)" if ocupada else "(Libre)"
            
            data.append({
                'id': u.id_ubicacion_warehouse,
                'texto': f"Fila {u.fila} - Col {u.columna} {estado_str}",
                'ocupada': ocupada
            })
            
        return JsonResponse({'posiciones': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)