"""
ASGI config for water_delivery project.

Expone la variable ASGI application para servidores compatibles (Daphne, Uvicorn, etc).
"""

import os

from django.core.asgi import get_asgi_application

# Configuración del entorno y obtención de la aplicación ASGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_delivery.settings')

application = get_asgi_application()
