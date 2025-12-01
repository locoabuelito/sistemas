from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_reg_maq, name="view_reg_maq"),
]