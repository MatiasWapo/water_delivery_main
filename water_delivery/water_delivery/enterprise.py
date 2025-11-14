# =============================================
# CONFIGURACIÓN EMPRESARIAL PRIVADA
# =============================================
# Configuración específica para despliegue empresarial con acceso restringido

import os
from decouple import config
from .settings import *

# =====================
# Configuración de Seguridad Empresarial
# =====================
DEBUG = False
SECRET_KEY = config('SECRET_KEY')

# IPs permitidas de la empresa (configurar según necesidad)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
ALLOWED_IPS = config('ALLOWED_IPS', default='127.0.0.1').split(',')

# Dominio de email de la empresa
COMPANY_DOMAIN = config('COMPANY_DOMAIN', default='')

# =====================
# Configuración de Base de Datos
# =====================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# =====================
# Configuración de Archivos Estáticos
# =====================
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =====================
# Configuración de Seguridad Adicional
# =====================
# Headers de seguridad
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de sesiones seguras
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hora

# =====================
# Configuración de Logging Empresarial
# =====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[ENTERPRISE] {levelname} {asctime} {module} {process:d} {thread:d} {ip} {user} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {ip} {user} {action}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'enterprise.log'),
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'security',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# =====================
# Configuración de Email Empresarial
# =====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# =====================
# Configuración de Backup Automático
# =====================
BACKUP_CONFIG = {
    'BACKUP_ENABLED': config('BACKUP_ENABLED', default=True, cast=bool),
    'BACKUP_FREQUENCY': config('BACKUP_FREQUENCY', default='daily'),
    'BACKUP_RETENTION': config('BACKUP_RETENTION', default=30, cast=int),  # días
    'BACKUP_PATH': config('BACKUP_PATH', default='/backups'),
}

# =====================
# Configuración de Monitoreo
# =====================
MONITORING_CONFIG = {
    'HEALTH_CHECK_ENABLED': True,
    'PERFORMANCE_MONITORING': True,
    'ERROR_TRACKING': True,
    'UPTIME_MONITORING': True,
}

# =====================
# Configuración de Auditoría
# =====================
AUDIT_CONFIG = {
    'LOG_USER_ACTIONS': True,
    'LOG_ADMIN_ACTIONS': True,
    'LOG_DATA_CHANGES': True,
    'AUDIT_RETENTION_DAYS': 365,
}

# =====================
# Configuración de Rate Limiting
# =====================
RATE_LIMIT_CONFIG = {
    'ENABLED': True,
    'DEFAULT_LIMIT': '100/hour',
    'LOGIN_LIMIT': '5/minute',
    'API_LIMIT': '1000/hour',
}

# =====================
# Configuración de VPN/Acceso Remoto
# =====================
VPN_CONFIG = {
    'VPN_REQUIRED': config('VPN_REQUIRED', default=False, cast=bool),
    'VPN_IPS': config('VPN_IPS', default='').split(','),
    'REMOTE_ACCESS_ENABLED': config('REMOTE_ACCESS_ENABLED', default=True, cast=bool),
}

# =====================
# Configuración de Dominio Personalizado
# =====================
CUSTOM_DOMAIN = config('CUSTOM_DOMAIN', default='')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)
    ALLOWED_HOSTS.append(f'www.{CUSTOM_DOMAIN}')

# =====================
# Configuración de Certificados SSL
# =====================
SSL_CONFIG = {
    'SSL_ENABLED': True,
    'SSL_CERT_PATH': config('SSL_CERT_PATH', default=''),
    'SSL_KEY_PATH': config('SSL_KEY_PATH', default=''),
    'FORCE_HTTPS': True,
} 