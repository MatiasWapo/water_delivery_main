"""
Middleware de acceso por dispositivo.

Permite restringir el acceso a la aplicación a un conjunto de dispositivos
autorizados mediante tokens estáticos definidos por variable de entorno
`DEVICE_TOKENS`. Útil cuando hay una cantidad limitada de equipos.

Cómo funciona:
- Define en variables de entorno: DEVICE_TOKENS=token1,token2,token3
- Cada dispositivo autorizado debe enviar el token en:
  - Cookie: DEVICE_TOKEN=<token>
  - o Header: X-Device-Token: <token>

Nota: Para mayor seguridad a largo plazo, conviene migrar a una solución
con registro de dispositivos en DB y tokens rotativos por usuario.
"""

from decouple import config
from django.http import HttpResponseForbidden


DEVICE_TOKENS = [t.strip() for t in config('DEVICE_TOKENS', default='').split(',') if t.strip()]


class DeviceTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si no hay tokens configurados, no aplicar restricción
        if not DEVICE_TOKENS:
            return self.get_response(request)

        token = (
            request.COOKIES.get('DEVICE_TOKEN')
            or request.headers.get('X-Device-Token')
        )

        if token not in DEVICE_TOKENS:
            return HttpResponseForbidden(
                '<h1>Acceso restringido</h1>'
                '<p>Este dispositivo no está autorizado para acceder al sistema.</p>'
            )

        return self.get_response(request)
