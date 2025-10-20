# =============================================
# MIDDLEWARE DE AUTENTICACIÓN GLOBAL
# =============================================
# Este middleware fuerza que todas las páginas requieran login, excepto las rutas
# públicas (login, registro, recuperación, admin, etc). Si el usuario no está autenticado
# y la URL no es pública, lo redirige al login.

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Device

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
            '/usuarios/login/',
            '/usuarios/register/',
            '/usuarios/recuperar/',
            '/usuarios/resetear/',
            '/admin/',
            '/usuarios/device/login/',
            '/usuarios/device/logout/',
            '/static/',
        ]
        # Si el usuario no está autenticado y la URL no es pública, redirige al login
        if not request.user.is_authenticated:
            if not any(request.path.startswith(path) for path in exempt_paths):
                return redirect('usuarios:login')
        # Si está autenticado o la URL es pública, continúa normalmente
        response = self.get_response(request)
        return response


class DeviceDBMiddleware:
    """
    Middleware que bloquea el acceso si el dispositivo no está autorizado en la DB.
    Permite acceso a rutas públicas (login de usuario, login de dispositivo, admin, estáticos).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        )

        if path.startswith(exempt_prefixes):
            return self.get_response(request)

        # Obtener token desde cookie o header
        token = request.COOKIES.get('DEVICE_TOKEN') or request.headers.get('X-Device-Token')

        if not token:
            return HttpResponseForbidden('<h1>Acceso restringido</h1><p>Dispositivo no autorizado (falta token).</p>')

        try:
            device = Device.objects.get(token=token, active=True)
            device.last_seen = timezone.now()
            device.save(update_fields=['last_seen'])
        except Device.DoesNotExist:
            return HttpResponseForbidden('<h1>Acceso restringido</h1><p>Este dispositivo no está autorizado o fue desactivado.</p>')

        return self.get_response(request)
