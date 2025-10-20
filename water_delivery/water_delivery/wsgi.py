"""
WSGI config for water_delivery project.

Expone la variable WSGI application para servidores compatibles (gunicorn, uWSGI, etc).
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Añadir el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Configuración del entorno y obtención de la aplicación WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_delivery.settings')

# Cargar la aplicación WSGI
try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise
