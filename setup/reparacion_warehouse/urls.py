# reparacion_warehouse/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ==========================================================================
    # 1. VISTA PRINCIPAL (HTML)
    # ==========================================================================
    path('', views.reparacion_warehouse_view, name='reparacion_warehouse'),

    # ==========================================================================
    # 2. APIS DE FILTROS (SELECTS EN CASCADA)
    # Rutas para llenar los dropdowns de Racks y Equipos dinámicamente
    # ==========================================================================
    path('api/obtener-racks/', views.obtener_racks_por_warehouse, name='obtener_racks_por_warehouse'),
    path('api/obtener-equipos/', views.obtener_equipos_por_warehouse, name='obtener_equipos_por_warehouse'),

    # ==========================================================================
    # 3. APIS DE GESTIÓN (CRUD SOLICITUDES)
    # Rutas para Crear, Leer, Actualizar y Borrar (Ocultar) solicitudes
    # ==========================================================================
    path('api/listar-solicitudes/', views.listar_solicitudes, name='listar_solicitudes'),
    path('api/crear-solicitud/', views.crear_solicitud, name='crear_solicitud'),
    
    # ¡OJO! Agregué esta línea porque la función 'editar_solicitud' existía en tu views.py
    path('api/editar-solicitud/', views.editar_solicitud, name='editar_solicitud'),

    # Esta ruta recibe el ID en la URL porque la vista así lo requiere
    path('api/ocultar-solicitud/<int:id_solicitud>/', views.ocultar_solicitud, name='ocultar_solicitud'),
    
    # Esta ruta recepciona un equipo (cambia estado de la solicitud)
    path('api/recepcionar-equipo/', views.recepcionar_equipo, name='recepcionar_equipo'),
    
    # Esta ruta permite asignar una ubicación física (Rack) al equipo
    path('api/obtener-posiciones/', views.obtener_posiciones_rack, name='obtener_posiciones_rack'),
    
    # --- NUEVAS RUTAS LABORATORIO ---
    path('laboratorio/', views.laboratorio_view, name='laboratorio_view'), # Pantalla del Técnico
    path('api/lab-iniciar/', views.iniciar_reparacion, name='lab_iniciar'),
    path('api/lab-finalizar/', views.finalizar_reparacion, name='lab_finalizar'),
]