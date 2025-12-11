from django.shortcuts import render
# Importamos el modelo Equipos desde la app de inventario
from inventario.models import Equipos 
from django.http import JsonResponse
from django.db.models import Q

def prestamos_view(request):
    # Traemos solo los equipos activos para que la lista no se llene de basura
    # Usamos .filter(activo_equipos=True) basado en tu columna 'activo_equipos'
    equipos = Equipos.objects.filter(activo_equipos=True).order_by('objeto')
    
    context = {
        'equipos': equipos
    }
    return render(request, 'prestamos/prestamos_herramientas.html', context)
    
def buscar_equipos(request):
    query = request.GET.get('q', '')
    payload = []
    
    if query:
        equipos = Equipos.objects.filter(
            Q(serial_number__icontains=query) | 
            Q(marca__icontains=query) |
            Q(objeto__icontains=query)
        )[:10]
        
        for equipo in equipos:
            # Separamos los datos para mostrarlos mejor en el frontend
            payload.append({
                'id': equipo.id_equipos,
                'texto_principal': f"{equipo.objeto} - {equipo.marca}",
                'texto_secundario': f"S/N: {equipo.serial_number}",
                'serial': equipo.serial_number
            })
    
    return JsonResponse({'results': payload})