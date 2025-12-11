# prestamos/urls.py
from django.urls import path
from . import views


urlpatterns = [
     path('', views.prestamos_view, name='prestamos'),
     path('buscar-equipos/', views.buscar_equipos, name='buscar_equipos'),
]