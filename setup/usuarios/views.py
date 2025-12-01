# usuarios/views.py
import logging
import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from .forms import UsuarioTecnicoLoginForm

# Obtener el logger
logger = logging.getLogger('usuarios')

@never_cache
@csrf_protect
def login_view(request):
    logger.debug(f"Iniciando proceso de login - User authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        logger.info(f"Usuario ya autenticado, redirigiendo: {request.user}")
        return redirect('usuarios:menu_principal')
    
    # Inicializar form para GET request
    form = UsuarioTecnicoLoginForm()
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        logger.debug("Procesando POST request de login")
        start_time = time.time()
        
        form = UsuarioTecnicoLoginForm(data=request.POST)
        logger.debug(f"Formulario creado - Válido: {form.is_valid()}")
        
        if form.is_valid():
            t_valid = time.time()
            validation_time = t_valid - start_time
            logger.debug(f"Validación de formulario: {validation_time:.4f}s")

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            t_before_auth = time.time()
            logger.debug(f"Intentando autenticar usuario: {username}")
            
            user = authenticate(request, username=username, password=password)
            
            t_after_auth = time.time()
            auth_time = t_after_auth - t_before_auth
            logger.debug(f"Tiempo de autenticación (DB query + hash): {auth_time:.4f}s - Usuario: {user.correo_tecnico if user else 'None'}")
            
            if user is not None:
                if user.is_active:
                    t_before_login = time.time()
                    login(request, user)
                    t_after_login = time.time()
                    session_time = t_after_login - t_before_login
                    logger.info(f"Creación de sesión: {session_time:.4f}s")
                    
                    total_time = time.time() - start_time
                    logger.info(f"Login exitoso completo - Usuario: {user.nombre_tecnico} - Tiempo total: {total_time:.4f}s")
                    
                    messages.success(request, f'¡Bienvenido {user.nombre_tecnico}!')
                    
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url:
                        logger.debug(f"Redirigiendo a: {next_url}")
                        return redirect(next_url)
                    
                    logger.debug("Redirigiendo a menú principal")
                    return redirect('usuarios:menu_principal')
                else:
                    logger.warning(f"Intento de login con cuenta inactiva: {username}")
                    messages.error(request, 'Tu cuenta está inactiva.')
            else:
                logger.warning(f"Autenticación fallida para usuario: {username}")
                messages.error(request, 'Correo electrónico o contraseña incorrectos.')
        else:
            logger.warning(f"Formulario inválido - Errores: {form.errors}")
            messages.error(request, 'Por favor corrige los errores a continuación.')
            
        total_time = time.time() - start_time
        logger.debug(f"Tiempo total proceso login (fallido/inválido): {total_time:.4f}s")
    
    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': next_url
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:login')  # Con namespace


@login_required
def menu_principal(request):
    logger.debug(f"Accediendo al menú principal - Usuario: {request.user.nombre_tecnico}")
    
    user = request.user
    user_info = {
        'nombre_tecnico': user.nombre_tecnico,
        'correo_tecnico': user.correo_tecnico,
        'sector': user.id_sector_tecnico.nombre_sector if user.id_sector_tecnico else 'Sin sector'
    }
    
    logger.debug(f"Información de usuario preparada: {user_info}")
    return render(request, 'menu_principal/menu_principal.html', {'user_info': user_info})