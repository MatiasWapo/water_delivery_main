"""
WSGI config for water_delivery project.
This file makes it easier to run the application with gunicorn.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_delivery.settings')

# Import and return the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
