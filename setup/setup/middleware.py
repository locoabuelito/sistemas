# setup/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages

class FiltroSeguridadInventarioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # --- LISTA BLANCA (Rutas permitidas para todos) ---
        self.rutas_permitidas = [
            '/admin/',           # Panel de admin
            '/usuarios/login/',           # Tu URL de login
            '/logout/',          # Tu URL de logout
            # Agrega aquí otras rutas que NO necesiten filtro de sector
        ]

    def __call__(self, request):
        path = request.path_info

        # 1. Si la ruta está en la lista blanca, dejar pasar.
        for ruta in self.rutas_permitidas:
            if path.startswith(ruta):
                return self.get_response(request)

        # 2. Si el usuario no está logueado, mandar al login.
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # 3. Si es Superusuario, acceso total.
        if request.user.is_superuser:
            return self.get_response(request)

        # 4. Lógica de SECTOR (Específica para "Depósito")
        tiene_permiso = False
        
        # Verificamos si el usuario tiene asignado un sector
        if hasattr(request.user, 'id_sector_tecnico') and request.user.id_sector_tecnico:
            nombre_sector = request.user.id_sector_tecnico.nombre_sector.lower()
            
            # Buscamos si es del área de depósito
            if 'depósito' in nombre_sector or 'deposito' in nombre_sector:
                tiene_permiso = True

        if tiene_permiso:
            return self.get_response(request)
        else:
            # Si no tiene permiso, mostrar error y sacar de ahí
            messages.error(request, "⛔ Acceso restringido al área de Depósito.")
            # Asegúrate de que '/inicio/' o la ruta a la que rediriges exista en la lista blanca o sea accesible
            return redirect('/usuarios/login/') # O redirigir a donde prefieras