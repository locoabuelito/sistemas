# reparacion_warehouse/urls.py
from django.urls import path
from . import views


urlpatterns = [
     path('', views.reparacion_warehouse_view, name='reparacion_warehouse'),
     # --- NUEVA RUTA PARA AJAX ---
     # Esta es la dirección que usaremos en el fetch: /reparacion-warehouse/api/obtener-equipos/
     path('api/obtener-equipos/', views.obtener_equipos_por_warehouse, name='obtener_equipos_por_warehouse'),
     # --- NUEVA RUTA PARA RACKS ---
     path('api/obtener-racks/', views.obtener_racks_por_warehouse, name='obtener_racks_por_warehouse'),
]