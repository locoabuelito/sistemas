
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def view_menu_principal(request):
    user_info = {
        'nombre_tecnico': request.user.nombre_tecnico,
        'correo_tecnico': request.user.correo_tecnico,
        'sector': request.user.id_sector_tecnico.nombre_sector if request.user.id_sector_tecnico else 'Sin sector'
    }
    return render(request, 'menu_principal/menu_principal.html', {'user_info': user_info})

# Vistas placeholder para las diferentes secciones
def reparacion_warehouse(request):
    return render(request, 'menu_principal/reparacion_warehouse.html')

def reparacion_hydro(request):
    return render(request, 'menu_principal/reparacion_hydro.html')

def historial_reparaciones(request):
    return render(request, 'menu_principal/historial_reparaciones.html')

def informes_warehouse(request):
    return render(request, 'menu_principal/informes_warehouse.html')

def informes_hydro(request):
    return render(request, 'menu_principal/informes_hydro.html')

def prestamos_herramientas(request):
    return render(request, 'menu_principal/prestamos_herramientas.html')

def control_inventarios(request):
    return render(request, 'menu_principal/control_inventarios.html')