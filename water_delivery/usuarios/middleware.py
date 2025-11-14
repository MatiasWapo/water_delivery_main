# =============================================
# MIDDLEWARE DE AUTENTICACIÓN GLOBAL
# =============================================
# Este middleware fuerza que todas las páginas requieran login, excepto las rutas
# públicas (login, registro, recuperación, admin, etc). Si el usuario no está autenticado
# y la URL no es pública, lo redirige al login.

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import logout
from urllib.parse import urlencode

class LoginRequiredMiddleware:
    """
    Middleware personalizado que exige autenticación en todas las páginas,
    excepto en las rutas exentas definidas en 'exempt_paths'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs que NO requieren login (páginas públicas)
        exempt_paths = [
            '/',  # Raíz del sitio
            '/usuarios/login/',
            '/usuarios/register/',
            '/usuarios/recuperar/',
            '/usuarios/resetear/',
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/.well-known/',
        ]
        
        # Evitar bucles: si ya estamos en login, no redirigir de nuevo
        if request.path.startswith('/usuarios/login/'):
            response = self.get_response(request)
            return response
        
        # Si el usuario no está autenticado y la URL no es pública, redirige al login
        # Manejar casos de sesión corrupta o expirada verificando is_authenticated de forma segura
        is_authenticated = False
        session_expired = False
        
        try:
            is_authenticated = request.user.is_authenticated
        except Exception:
            # Si hay error al verificar autenticación (sesión corrupta o expirada)
            session_expired = True
            is_authenticated = False
        
        # Si la sesión está expirada o corrupta, hacer logout explícito y limpiar sesión
        if session_expired:
            try:
                # Verificar si hay una sesión activa pero expirada
                if hasattr(request, 'session') and request.session.session_key:
                    # Hacer logout para limpiar la sesión del usuario
                    logout(request)
                    # Limpiar la sesión completamente
                    request.session.flush()
            except Exception:
                # Si hay error al hacer logout, intentar limpiar la sesión de todas formas
                try:
                    if hasattr(request, 'session'):
                        request.session.flush()
                except Exception:
                    pass
        
        if not is_authenticated:
            if not any(request.path.startswith(path) for path in exempt_paths):
                # Evitar bucle: verificar que no estemos ya redirigiendo a login
                login_url = reverse('usuarios:login')
                if request.path != login_url:
                    # Redirigir a login sin parámetros (sin next)
                    return redirect('usuarios:login')
        
        # Si está autenticado o la URL es pública, continúa normalmente
        response = self.get_response(request)
        return response


class DeviceDBMiddleware:
    """
    Middleware que bloquea el acceso si el dispositivo no está autorizado en la DB.
    Permite acceso a rutas públicas (login de usuario, login de dispositivo, admin, estáticos).
    En desarrollo (DEBUG=True), no aplica restricciones.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # En desarrollo, no aplicar restricciones
        # También verificar si estamos en localhost para desarrollo local
        # FORZAR desactivación en localhost/127.0.0.1 para evitar bucles
        try:
            host = request.get_host().split(':')[0].lower()  # Remover puerto y convertir a minúsculas
            is_localhost = host in ('127.0.0.1', 'localhost', '::1')
        except:
            is_localhost = False
        
        # Si estamos en DEBUG o localhost, NO aplicar restricciones de dispositivo
        if settings.DEBUG or is_localhost:
            return self.get_response(request)
        
        path = request.path
        exempt_prefixes = (
            '/usuarios/login/',
            '/usuarios/register/',
            '/usuarios/recuperar/',
            '/usuarios/resetear/',
            '/usuarios/device/login/',
            '/usuarios/device/logout/',
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
        )

        # Verificar si la ruta comienza con algún prefijo exento
        # Si está exenta, permitir el acceso sin verificar token
        if any(path.startswith(prefix) for prefix in exempt_prefixes):
            return self.get_response(request)
        
        # IMPORTANTE: Solo verificar token de dispositivo si el usuario está autenticado
        # Si no está autenticado, dejar que LoginRequiredMiddleware maneje la redirección
        try:
            is_authenticated = request.user.is_authenticated
        except Exception:
            # Si hay error al verificar autenticación (sesión corrupta), no verificar token
            return self.get_response(request)
        
        if not is_authenticated:
            return self.get_response(request)

        # Obtener token desde cookie o header
        token = request.COOKIES.get('DEVICE_TOKEN') or request.headers.get('X-Device-Token')

        if not token:
            # Redirigir al login de dispositivo con la URL actual como parámetro 'next'
            device_login_url = reverse('usuarios:device_login')
            next_path = request.path
            
            # Evitar bucle: no redirigir si ya estamos en la ruta de login de dispositivo
            if path.startswith(device_login_url):
                return self.get_response(request)
            
            # Evitar bucle: no redirigir si el next apunta a la misma ruta actual
            # (esto indicaría un bucle infinito)
            next_param = request.GET.get('next', '')
            if next_param == next_path or next_param == path:
                # Si hay un bucle, redirigir a device_login sin parámetro next
                return redirect(device_login_url)
            
            # Verificar si el parámetro 'next' en la query string apunta a device_login
            # para evitar bucles cuando se redirige múltiples veces
            if next_param and next_param.startswith(device_login_url):
                # Si el next apunta a device_login, redirigir sin parámetro next
                return redirect(device_login_url)
            
            redirect_url = f'{device_login_url}?{urlencode({"next": next_path})}'
            return redirect(redirect_url)

        try:
            device = Device.objects.get(token=token, active=True)
            device.last_seen = timezone.now()
            device.save(update_fields=['last_seen'])
        except Device.DoesNotExist:
            # Token inválido o dispositivo desactivado
            # Redirigir al login de dispositivo
            device_login_url = reverse('usuarios:device_login')
            next_path = request.path
            
            # Evitar bucle: no redirigir si ya estamos en la ruta de login de dispositivo
            if path.startswith(device_login_url):
                return self.get_response(request)
            
            # Verificar si el parámetro 'next' en la query string apunta a device_login
            # para evitar bucles cuando se redirige múltiples veces
            next_param = request.GET.get('next', '')
            if next_param and next_param.startswith(device_login_url):
                # Si el next apunta a device_login, redirigir sin parámetro next
                return redirect(device_login_url)
            
            redirect_url = f'{device_login_url}?{urlencode({"next": next_path})}'
            return redirect(redirect_url)

        return self.get_response(request)
