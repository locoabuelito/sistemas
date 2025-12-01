# reparacion_warehouse/urls.py
from django.urls import path
from . import views


urlpatterns = [
     path('reparacion-warehouse/', views.reparacion_warehouse_view, name='reparacion_warehouse'),
]