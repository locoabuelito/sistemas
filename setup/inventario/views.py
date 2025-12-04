# inventario/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Equipos, TipoSistema, UbicacionDeposito
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def registrar_equipo(request):
    try:
        # 1. Obtener datos del FormData enviado por JS
        objeto = request.POST.get('objeto')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        id_sistema = request.POST.get('sistema')
        id_ubicacion = request.POST.get('ubicacion')
        stock_min = request.POST.get('stock_min')
        seriales_texto = request.POST.get('seriales')
        
        # 2. Obtener el ID del usuario logueado automáticamente
        # Asumiendo que tu usuario tiene un campo 'id_usuario_tecnico' o usas el PK
        id_usuario_actual = request.user.pk 

        # 3. Validaciones básicas
        if not all([objeto, marca, modelo, id_sistema, id_ubicacion, seriales_texto]):
            return JsonResponse({'status': 'error', 'message': 'Faltan datos obligatorios'}, status=400)

        # 4. Procesar seriales (uno por línea)
        lista_seriales = [s.strip() for s in seriales_texto.split('\n') if s.strip()]
        
        cantidad_creados = 0
        
        # 5. Iterar y crear cada equipo
        for serial in lista_seriales:
            nuevo_equipo = Equipos(
                objeto=objeto,
                marca=marca,
                modelo=modelo,
                serial_number=serial,
                id_tipo_sistema_id=int(id_sistema),      # Asignar ID sistema
                id_ubicacion_deposito_id=int(id_ubicacion), # Asignar ID ubicación
                stock_min=int(stock_min) if stock_min else 0,
                
                # ASIGNACIÓN AUTOMÁTICA DEL USUARIO
                id_usuario_tecnico=id_usuario_actual,
                
                activo_equipos=True,
            )
            nuevo_equipo.save()
            cantidad_creados += 1

        return JsonResponse({
            'status': 'success', 
            'message': f'Se registraron {cantidad_creados} equipos correctamente.'
        })

    except Exception as e:
        print(f"❌ Error al registrar equipo: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def control_inventarios(request):
    try:
        # 1. Obtener filtros
        marca_filtro = request.GET.get('marca', '')
        busqueda_filtro = request.GET.get('busqueda', '')
        sistema_filtro = request.GET.get('sistema', '')
        items_por_pagina = int(request.GET.get('items', 10))

        # 2. Consulta Base (Solo equipos activos)
        equipos_query = Equipos.objects.filter(activo_equipos=True)

        # 3. Aplicar Filtros
        if marca_filtro:
            equipos_query = equipos_query.filter(marca__icontains=marca_filtro)
        
        if sistema_filtro:
            equipos_query = equipos_query.filter(id_tipo_sistema_id=sistema_filtro)

        if busqueda_filtro:
            equipos_query = equipos_query.filter(
                Q(objeto__icontains=busqueda_filtro) |
                Q(modelo__icontains=busqueda_filtro)
                # Quitamos serial porque ahora agrupamos
            )

        # 4. AGRUPAR Y CONTAR (Aquí está el cambio clave)
        # Esto le dice a la DB: "Junta todo lo que tenga mismo Objeto, Marca, Modelo y Stock Min"
        # y crea un campo nuevo llamado 'cantidad'
        equipos_agrupados = equipos_query.values(
            'objeto', 'marca', 'modelo', 'stock_min', 'id_tipo_sistema__nombre_sistema'
        ).annotate(
            cantidad=Count('id_equipos')
        ).order_by('objeto', 'marca', 'modelo')

        # 5. Paginación
        paginator = Paginator(equipos_agrupados, items_por_pagina)
        page = request.GET.get('page', 1)

        try:
            equipos_paginados = paginator.page(page)
        except PageNotAnInteger:
            equipos_paginados = paginator.page(1)
        except EmptyPage:
            equipos_paginados = paginator.page(paginator.num_pages)

        # 6. Datos Extra para los selectores (Filtros del HTML)
        # Estas consultas son para llenar las opciones de búsqueda
        todas_marcas = list(Equipos.objects.filter(activo_equipos=True).exclude(marca__isnull=True).exclude(marca='').values_list('marca', flat=True).distinct().order_by('marca'))
        todos_modelos = list(Equipos.objects.filter(activo_equipos=True).exclude(modelo__isnull=True).exclude(modelo='').values_list('modelo', flat=True).distinct().order_by('modelo'))
        todos_tipos_maquina = list(Equipos.objects.filter(activo_equipos=True).exclude(objeto__isnull=True).exclude(objeto='').values_list('objeto', flat=True).distinct().order_by('objeto'))
        sistemas_reparacion = TipoSistema.objects.filter(activo_sistema=True).order_by('nombre_sistema')
        
        # Estadísticas generales
        total_equipos = Equipos.objects.filter(activo_equipos=True).count()
        equipos_activos = Equipos.objects.filter(activo_equipos=True).count()
        marcas_unicas = Equipos.objects.filter(activo_equipos=True).values('marca').distinct().count()
        sistemas_unicos = Equipos.objects.filter(activo_equipos=True).exclude(id_tipo_sistema__isnull=True).values('id_tipo_sistema').distinct().count()

        # Carga de Técnicos (Tu código original mantenido)
        tecnicos_activos = []
        try:
            from usuarios.models import UsuarioTecnico
            tecnicos_activos = UsuarioTecnico.objects.filter(activo_tecnico=True).select_related('id_sector_tecnico').order_by('nombre_tecnico')
        except ImportError:
            pass

        ubicaciones_deposito = UbicacionDeposito.objects.filter(ubicacion_activo=True).order_by('nombre_pallet', 'nombre_caja')

        # 7. Contexto
        contexto = {
            'equipos': equipos_paginados, # Ahora lleva el conteo agrupado
            'total_equipos': total_equipos,
            'marcas_unicas': marcas_unicas,
            'sistemas_unicos': sistemas_unicos,
            'equipos_activos': equipos_activos,
            'marca_filtro': marca_filtro,
            'busqueda_filtro': busqueda_filtro,
            'sistema_filtro': sistema_filtro,
            'todas_marcas': todas_marcas,
            'todos_modelos': json.dumps(todos_modelos),
            'todos_tipos_maquina': json.dumps(todos_tipos_maquina),
            'sistemas_reparacion': sistemas_reparacion,
            'tecnicos': tecnicos_activos,
            'ubicaciones_deposito': ubicaciones_deposito,
            'paginator': paginator,
            'items_por_pagina': items_por_pagina,
            'opciones_items': [10, 20, 50, 100],
        }

        return render(request, 'inventario/control_inventarios.html', contexto)

    except Exception as e:
        print(f"Error: {e}")
        # En caso de error, mostramos tabla vacía pero evitamos que la pagina se rompa
        return render(request, 'inventario/control_inventarios.html', {'equipos': [], 'error': str(e)})

# Vista para búsqueda en tiempo real
def buscar_sugerencias(request):
    termino = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    
    if not termino or not tipo:
        return JsonResponse({'sugerencias': []})
    
    try:
        if tipo == 'marca':
            sugerencias = Equipos.objects.filter(
                activo_equipos=True,
                marca__icontains=termino
            ).values_list('marca', flat=True).distinct().order_by('marca')[:10]
            
        elif tipo == 'busqueda':
            sugerencias = Equipos.objects.filter(
                activo_equipos=True
            ).filter(
                Q(objeto__icontains=termino) |
                Q(modelo__icontains=termino) |
                Q(serial_number__icontains=termino)
            ).values_list('modelo', flat=True).distinct().order_by('modelo')[:10]
            
        else:
            sugerencias = []
        
        return JsonResponse({
            'sugerencias': list(sugerencias),
            'termino': termino,
            'tipo': tipo
        })
        
    except Exception as e:
        return JsonResponse({'sugerencias': [], 'error': str(e)})
    
@require_POST
def crear_ubicacion(request):
    try:
        # Obtener datos del POST
        id_sistema = request.POST.get('sistema')
        pallet = request.POST.get('pallet')
        caja = request.POST.get('caja')
        
        # Validar datos básicos
        if not id_sistema or not pallet or not caja:
            return JsonResponse({
                'status': 'error', 
                'message': 'Faltan datos obligatorios'
            }, status=400)

        # Crear la ubicación
        # Nota: Usamos id_tipo_sistema como entero según tu modelo actual
        nueva_ubicacion = UbicacionDeposito(
            id_tipo_sistema=int(id_sistema), 
            nombre_pallet=pallet,
            nombre_caja=caja,
            ubicacion_activo=True
        )
        nueva_ubicacion.save()

        return JsonResponse({
            'status': 'success', 
            'message': f'Ubicación P:{pallet} - C:{caja} creada correctamente'
        })

    except Exception as e:
        print(f"Error al crear ubicación: {str(e)}")
        return JsonResponse({
            'status': 'error', 
            'message': f'Error interno: {str(e)}'
        }, status=500)