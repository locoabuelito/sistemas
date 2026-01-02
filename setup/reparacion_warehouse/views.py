# reparacion_warehouse/views.py

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import F
from django.db import transaction

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
        ).order_by('id_ubicacion_warehouse__fila', 'id_ubicacion_warehouse__columna')
        
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
        # 1. Obtenemos las solicitudes activas
        solicitudes = SolicitudReparacion.objects.filter(
            solicitud_activa=True
        ).select_related('equipo', 'tecnico', 'tipo_problema').order_by('-fecha_creacion')

        data = []
        for s in solicitudes:
            fecha_local = timezone.localtime(s.fecha_creacion)
            fecha_fmt = fecha_local.strftime('%d/%m/%Y %H:%M')
            
            # Nombre técnico seguro
            nombre_tec = "Técnico"
            if s.tecnico:
                nombre_tec = getattr(s.tecnico, 'nombre_tecnico', getattr(s.tecnico, 'nombre', str(s.tecnico)))

            # -------------------------------------------------------
            # NUEVA LÓGICA DE UBICACIÓN (CORRECCIÓN)
            # -------------------------------------------------------
            ubicacion_str = "Bodega / Tránsito"
            
            # Buscamos el ÚLTIMO movimiento registrado de este equipo (sea activo o inactivo)
            # Ordenamos por id_asignacion descendente para obtener el más reciente.
            ultimo_movimiento = AsignacionUbicacionWarehouse.objects.filter(
                id_equipos_warehouse=s.equipo
            ).select_related('id_ubicacion_warehouse__id_ubicacion').order_by('-id_asignacion').first()

            if ultimo_movimiento and ultimo_movimiento.id_ubicacion_warehouse:
                wh_obj = ultimo_movimiento.id_ubicacion_warehouse
                nombre_wh = wh_obj.id_ubicacion.nombre_ubicacion
                
                # Construimos el string de ubicación
                base_str = f"{nombre_wh} ➝ Rack {wh_obj.rack} ➝ F:{wh_obj.fila}/C:{wh_obj.columna}"
                
                # Si la asignación está activa, es su ubicación actual.
                # Si está inactiva (porque se liberó al dañar), le agregamos "(Origen)" para que sepas de dónde vino.
                if ultimo_movimiento.activo_asignacion_equipo_ubicacion:
                    ubicacion_str = base_str
                else:
                    ubicacion_str = f"{base_str} (Origen)" 

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

# -------------------------------------------------------------------------
# VISTA: CREAR SOLICITUD (CON LIBERACIÓN AUTOMÁTICA DE RACK)
# -------------------------------------------------------------------------
@login_required
@require_POST
def crear_solicitud(request):
    try:
        # Convertimos el cuerpo de la petición JSON a un diccionario Python
        data = json.loads(request.body)
        
        # Usamos transaction.atomic para garantizar integridad:
        # Si falla la liberación del rack, NO se crea la solicitud, y viceversa.
        with transaction.atomic():
            
            # 1. CREAR EL REGISTRO DE LA SOLICITUD DE REPARACIÓN
            nueva_solicitud = SolicitudReparacion(
                equipo_id = data.get('equipo_id'),
                tecnico = request.user,
                tipo_problema_id = data.get('tipo_problema_id'),
                th_cantidad = data.get('th_cantidad'),
                descripcion = data.get('descripcion'),
                estado = 'pendiente', # Se inicia en pendiente (esperando llevar a laboratorio)
                solicitud_activa = True
            )
            nueva_solicitud.save()

            # 2. GESTIÓN DE INVENTARIO: LIBERAR LA UBICACIÓN ACTUAL
            # Buscamos si el equipo tiene una ubicación activa en este momento (en un Rack)
            asignacion_actual = AsignacionUbicacionWarehouse.objects.filter(
                id_equipos_warehouse_id=data.get('equipo_id'),
                activo_asignacion_equipo_ubicacion=True
            ).first()

            if asignacion_actual:
                # Si está en un rack, lo "sacamos" lógicamente.
                # Marcamos la asignación como inactiva (False) y ponemos fecha de fin.
                asignacion_actual.activo_asignacion_equipo_ubicacion = False
                asignacion_actual.fecha_desasignacion = timezone.now()
                
                # Agregamos una nota histórica para saber por qué salió del rack
                nota_salida = f"Retirado por Solicitud de Reparación #{nueva_solicitud.id_solicitud}"
                if asignacion_actual.observaciones:
                    asignacion_actual.observaciones += f" | {nota_salida}"
                else:
                    asignacion_actual.observaciones = nota_salida
                
                asignacion_actual.save()
                print(f"✅ Ubicación liberada para equipo {data.get('equipo_id')}")

        # Si todo sale bien (transaction.atomic no detectó errores), respondemos éxito
        return JsonResponse({
            'status': 'success', 
            'message': 'Solicitud creada y ubicación del equipo liberada correctamente.'
        })

    except Exception as e:
        # Si algo falla, transaction.atomic deshace cualquier cambio (rollback)
        print(f"❌ Error CRÍTICO al crear solicitud: {e}")
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
