# =============================================
# CONFIGURACIÓN DE SEGURIDAD PARA ACCESO PRIVADO
# =============================================
# Este archivo maneja la seguridad para acceso empresarial privado

import os
import logging
from decouple import config
from django.http import HttpResponseForbidden
from django.conf import settings

# =====================
# Configuración de IPs Permitidas
# =====================
ALLOWED_IPS = config('ALLOWED_IPS', default='127.0.0.1').split(',')

# =====================
# Middleware de Seguridad IP
# =====================
class IPRestrictionMiddleware:
    """
    Middleware para restringir acceso solo a IPs específicas de la empresa
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtener IP del cliente
        client_ip = self.get_client_ip(request)
        
        # Verificar si la IP está permitida
        if not self.is_ip_allowed(client_ip):
            return HttpResponseForbidden(
                '<h1>Acceso Denegado</h1>'
                '<p>Esta aplicación es de uso exclusivo para empleados de la empresa.</p>'
                '<p>Si crees que esto es un error, contacta al administrador del sistema.</p>'
            )
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """
        Obtiene la IP real del cliente, considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_allowed(self, client_ip):
        """
        Verifica si la IP del cliente está en la lista de permitidas
        """
        # Si no hay IPs configuradas, permitir todo (solo en desarrollo)
        if not ALLOWED_IPS or ALLOWED_IPS == ['127.0.0.1']:
            return True
        
        return client_ip in ALLOWED_IPS

# =====================
# Configuración de Autenticación Adicional
# =====================
def require_company_domain(user):
    """
    Verifica que el email del usuario pertenezca al dominio de la empresa
    """
    if not user.is_authenticated:
        return False
    
    # Dominio de la empresa (configurar según necesidad)
    company_domain = config('COMPANY_DOMAIN', default='')
    
    if not company_domain:
        return True  # Si no está configurado, permitir
    
    return user.email.endswith(f'@{company_domain}')

# =====================
# Configuración de Sesiones Seguras
# =====================
SECURE_SESSION_CONFIG = {
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Strict',
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
    'SESSION_COOKIE_AGE': 3600,  # 1 hora
}

# =====================
# Configuración de Headers de Seguridad
# =====================
SECURITY_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}

# =====================
# Configuración de Rate Limiting
# =====================
RATE_LIMIT_CONFIG = {
    'DEFAULT_RATE_LIMIT': '100/hour',
    'LOGIN_RATE_LIMIT': '5/minute',
    'API_RATE_LIMIT': '1000/hour',
}

# =====================
# Configuración de Logging de Seguridad
# =====================
SECURITY_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {ip} {user} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}