#!/usr/bin/env python
"""
Archivo de utilidad para tareas administrativas de Django.
Permite ejecutar comandos como runserver, makemigrations, migrate, etc.
"""
import os
import sys


def main():
    """
    Función principal: configura el entorno y ejecuta comandos de Django.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_delivery.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
