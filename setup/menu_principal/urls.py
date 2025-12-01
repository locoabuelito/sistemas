from django.urls import path

from . import views

app_name = 'menu_principal'

urlpatterns = [
    path("", views.view_menu_principal, name="view_menu_principal"),
    #path('reparacion-warehouse/', views.reparacion_warehouse, name='reparacion_warehouse'),
    path('reparacion-hydro/', views.reparacion_hydro, name='reparacion_hydro'),
    path('historial-reparaciones/', views.historial_reparaciones, name='historial_reparaciones'),
    path('informes-warehouse/', views.informes_warehouse, name='informes_warehouse'),
    path('informes-hydro/', views.informes_hydro, name='informes_hydro'),
    path('prestamos-herramientas/', views.prestamos_herramientas, name='prestamos_herramientas'),
    #path('control-inventarios/', views.control_inventarios, name='control_inventarios'),
]