# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('control-inventarios/', views.control_inventarios, name='control_inventarios'),
]