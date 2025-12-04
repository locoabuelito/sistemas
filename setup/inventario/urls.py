# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('control-inventarios/', views.control_inventarios, name='control_inventarios'),
    path('crear-ubicacion/', views.crear_ubicacion, name='crear_ubicacion'),
    path('registrar-equipo/', views.registrar_equipo, name='registrar_equipo'),
    
]