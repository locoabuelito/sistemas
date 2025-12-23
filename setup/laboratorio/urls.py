# laboratorio/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.laboratorio_dashboard, name='laboratorio_dashboard'),
    path('api/iniciar/', views.iniciar_reparacion, name='lab_iniciar'),
    path('api/finalizar/', views.finalizar_reparacion, name='lab_finalizar'),
]