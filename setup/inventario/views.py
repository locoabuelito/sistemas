# inventario/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from .models import Equipos, TipoSistema
import json

def control_inventarios(request):
    try:
        print("🚀 INICIANDO VISTA control_inventarios")
        
        # Obtener parámetros de filtro desde la URL
        marca_filtro = request.GET.get('marca', '')
        busqueda_filtro = request.GET.get('busqueda', '')
        sistema_filtro = request.GET.get('sistema', '')
        items_por_pagina = int(request.GET.get('items', 10))
        
        print(f"📊 Filtros recibidos - Marca: '{marca_filtro}', Búsqueda: '{busqueda_filtro}', Sistema: '{sistema_filtro}'")
        
        # Consulta base ordenada
        equipos_query = Equipos.objects.filter(activo_equipos=True).select_related('id_tipo_sistema').order_by('id_equipos')
        
        # Aplicar filtros si existen
        if marca_filtro:
            equipos_query = equipos_query.filter(marca__icontains=marca_filtro)
        
        if busqueda_filtro:
            equipos_query = equipos_query.filter(
                Q(objeto__icontains=busqueda_filtro) |
                Q(modelo__icontains=busqueda_filtro) |
                Q(serial_number__icontains=busqueda_filtro)
            )
        
        if sistema_filtro:
            equipos_query = equipos_query.filter(id_tipo_sistema_id=sistema_filtro)
        
        # Configurar paginación
        paginator = Paginator(equipos_query, items_por_pagina)
        page = request.GET.get('page', 1)
        
        try:
            equipos_paginados = paginator.page(page)
        except PageNotAnInteger:
            equipos_paginados = paginator.page(1)
        except EmptyPage:
            equipos_paginados = paginator.page(paginator.num_pages)
        
        # Obtener estadísticas
        total_equipos = equipos_query.count()
        marcas_unicas = equipos_query.values('marca').distinct().count()
        sistemas_unicos = equipos_query.exclude(id_tipo_sistema__isnull=True).values('id_tipo_sistema').distinct().count()
        
        # Obtener datos únicos para autocompletado
        todas_marcas = list(Equipos.objects.filter(activo_equipos=True)
                          .exclude(marca__isnull=True).exclude(marca='')
                          .values_list('marca', flat=True).distinct().order_by('marca'))
        
        todos_modelos = list(Equipos.objects.filter(activo_equipos=True)
                           .exclude(modelo__isnull=True).exclude(modelo='')
                           .values_list('modelo', flat=True).distinct().order_by('modelo'))
        
        todos_tipos_maquina = list(Equipos.objects.filter(activo_equipos=True)
                                 .exclude(objeto__isnull=True).exclude(objeto='')
                                 .values_list('objeto', flat=True).distinct().order_by('objeto'))
        
        # Obtener sistemas de reparación activos
        sistemas_reparacion = TipoSistema.objects.filter(activo_sistema=True).order_by('nombre_sistema')
        todos_sistemas = TipoSistema.objects.filter(activo_sistema=True).order_by('nombre_sistema')
        
        # ✅ CARGA DE TÉCNICOS CON MODELO SECTOR - CORREGIDO
        print("🔍 CARGANDO TÉCNICOS CON SECTOR...")
        tecnicos_activos = []
        
        try:
            from usuarios.models import UsuarioTecnico
            print("✅ Modelo UsuarioTecnico importado exitosamente")
            
            # CORRECCIÓN: Usar 'id_sector_tecnico' en lugar de 'sector'
            tecnicos_activos = UsuarioTecnico.objects.filter(
                activo_tecnico=True
            ).select_related('id_sector_tecnico').order_by('nombre_tecnico')
            
            print(f"✅ Técnicos activos cargados: {tecnicos_activos.count()}")
            
            # CORRECCIÓN: Usar 'id_sector_tecnico' en lugar de 'sector'
            for i, tecnico in enumerate(tecnicos_activos, 1):
                sector_nombre = tecnico.id_sector_tecnico.nombre_sector if tecnico.id_sector_tecnico else "Sin sector"
                print(f"   {i}. {tecnico.nombre_tecnico} - {tecnico.correo_tecnico} - Sector: {sector_nombre}")
                
        except ImportError as e:
            print(f"❌ ERROR DE IMPORTACIÓN: {e}")
        except Exception as e:
            print(f"❌ ERROR AL CARGAR TÉCNICOS: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
        
        # Preparar datos para el template
        contexto = {
            'equipos': equipos_paginados,
            'total_equipos': total_equipos,
            'equipos_activos': total_equipos,
            'marcas_unicas': marcas_unicas,
            'sistemas_unicos': sistemas_unicos,
            'marca_filtro': marca_filtro,
            'busqueda_filtro': busqueda_filtro,
            'sistema_filtro': sistema_filtro,
            'todas_marcas': json.dumps(list(todas_marcas)),
            'todos_modelos': json.dumps(list(todos_modelos)),
            'todos_tipos_maquina': json.dumps(list(todos_tipos_maquina)),
            'sistemas_reparacion': sistemas_reparacion,
            'todos_sistemas': todos_sistemas,
            'tecnicos': tecnicos_activos,
            'paginator': paginator,
            'items_por_pagina': items_por_pagina,
            'opciones_items': [10, 20, 50, 100],
        }
        
        print(f"✅ CONTEXTO PREPARADO - Técnicos enviados al template: {len(tecnicos_activos)}")
        print("🎯 RENDERIZANDO TEMPLATE...")
        
        return render(request, 'inventario/control_inventarios.html', contexto)
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en control_inventarios: {str(e)}")
        import traceback
        print(f"TRACEBACK COMPLETO: {traceback.format_exc()}")
        
        contexto = {
            'equipos': [],
            'total_equipos': 0,
            'equipos_activos': 0,
            'marcas_unicas': 0,
            'sistemas_unicos': 0,
            'todas_marcas': json.dumps([]),
            'todos_modelos': json.dumps([]),
            'todos_tipos_maquina': json.dumps([]),
            'sistemas_reparacion': [],
            'todos_sistemas': [],
            'tecnicos': [],
            'paginator': None,
            'items_por_pagina': 10,
            'opciones_items': [10, 20, 50, 100],
            'error': f"Error al cargar el inventario: {str(e)}"
        }
        return render(request, 'inventario/control_inventarios.html', contexto)

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