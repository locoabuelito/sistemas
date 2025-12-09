# prestamos/views.py

from django.shortcuts import render

def prestamos_view(request):
    return render(request, 'prestamos/prestamos_herramientas.html')
