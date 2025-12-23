# laboratorio/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

# IMPORTANTE: Importamos el modelo desde la app de origen
from reparacion_warehouse.models import SolicitudReparacion

# 1. VISTA HTML: Pantalla del Técnico
@login_required
def laboratorio_dashboard(request):
    # Nota el cambio de ruta del template
    return render(request, 'laboratorio/dashboard.html')

# 2. API: INICIAR TRABAJO
@login_required
@require_POST
def iniciar_reparacion(request):
    try:
        data = json.loads(request.body)
        solicitud = get_object_or_404(SolicitudReparacion, pk=data.get('id_solicitud'))
        
        if solicitud.estado != 'pendiente':
             return JsonResponse({'status': 'error', 'message': 'Solo pendientes'}, status=400)
             
        solicitud.estado = 'proceso'
        solicitud.save()
        
        return JsonResponse({'status': 'success', 'message': 'Iniciado'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# 3. API: FINALIZAR TRABAJO
@login_required
@require_POST
def finalizar_reparacion(request):
    try:
        data = json.loads(request.body)
        id_solicitud = data.get('id_solicitud')
        solucion = data.get('solucion_tecnica')
        
        if not solucion:
            return JsonResponse({'status': 'error', 'message': 'Detallar solución'}, status=400)

        solicitud = get_object_or_404(SolicitudReparacion, pk=id_solicitud)
        
        if solicitud.estado != 'proceso':
             return JsonResponse({'status': 'error', 'message': 'No está en proceso'}, status=400)

        solicitud.estado = 'reparado'
        solicitud.solucion_tecnica = solucion
        solicitud.save()
        
        return JsonResponse({'status': 'success', 'message': 'Finalizado'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)