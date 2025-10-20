# =============================================
# CONFIGURACIÓN PRINCIPAL DE DJANGO (settings.py)
# =============================================
# Define rutas, apps, seguridad, base de datos, internacionalización, archivos estáticos y email.
# ¡IMPORTANTE! Cambiar claves y opciones de seguridad en producción.
#
# Secciones principales:
# - Seguridad y rutas
# - Apps instaladas
# - Middleware
# - Templates
# - Base de datos
# - Validación de contraseñas
# - Internacionalización
# - Archivos estáticos
# - Email y seguridad

from pathlib import Path
import os 
from decouple import config
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(_file_).resolve().parent.parent

# =====================
# Seguridad y rutas
# =====================
# SECRET_KEY, DEBUG, ALLOWED_HOSTS
# Security settings (¡OJO! Cambiar en producción)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-a!d5f&34%4n*2^4c*&6^0v2d=*c0x)$j-o#mvde^7odl4p2mi-')
DEBUG = False
ALLOWED_HOSTS = [
    'ns.inversioneslos2ramirez.com', 
    'inversioneslos2ramirez.com',
    '84.247.168.85',
    'localhost',
    '127.0.0.1'
]

# =====================
# Apps instaladas
# =====================
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'clientes',
    'usuarios',
    'widget_tweaks',
] 

# =====================
# Configuración de Crispy Forms
# =====================
# Crispy Forms Config
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =====================
# Autenticación y usuario personalizado
# =====================
# Authentication Settings
AUTH_USER_MODEL = 'usuarios.Usuario'
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'clientes:lista_clientes'  
LOGOUT_REDIRECT_URL = 'usuarios:login'

# =====================
# Middleware
# =====================
# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS debe ir lo más arriba posible
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.LoginRequiredMiddleware',
    # Middleware de seguridad para acceso privado (solo en producción)
    'water_delivery.security.IPRestrictionMiddleware' if not DEBUG else None,
    # Middleware de control por dispositivo basado en base de datos
    'usuarios.middleware.DeviceDBMiddleware',
]
MIDDLEWARE = [m for m in MIDDLEWARE if m is not None]

ROOT_URLCONF = 'water_delivery.urls'

# =====================
# Templates y contexto
# =====================
# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'water_delivery.wsgi.application'

# =====================
# Base de datos
# =====================
# Database
import dj_database_url

# Configuración de base de datos
# Si existe DATABASE_URL/RAILWAY_DATABASE_URL/POSTGRES_URL (para Railway), la usa; si no, usa PostgreSQL local
DATABASE_URL = config('DATABASE_URL', default=None) or \
               config('RAILWAY_DATABASE_URL', default=None) or \
               config('POSTGRES_URL', default=None)

def _ensure_sslmode(url: str) -> str:
    try:
        parsed = urlparse(url)
        # Solo aplicar para postgres
        if parsed.scheme.startswith('postgres'):
            query = dict(parse_qsl(parsed.query))
            if 'sslmode' not in query:
                query['sslmode'] = 'require'
                new_query = urlencode(query)
                return urlunparse(parsed._replace(query=new_query))
    except Exception:
        pass
    return url

# Configuración de la base de datos para VPS Ubuntu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'water_delivery_db',
        'USER': 'postgres',
        'PASSWORD': 'matias123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# =====================
# Validación de contraseñas
# =====================
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Asegura contraseñas más seguras
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =====================
# Internacionalización
# =====================
# Internationalization
LANGUAGE_CODE = 'es-es'  # Cambiado a español
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# =====================
# Archivos estáticos
# =====================
# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/water_delivery_main/static/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/water_delivery_main/media/'

# =====================
# CORS
# =====================
# Configuración de CORS para permitir frontends externos si aplica
CORS_ALLOWED_ORIGINS = [o for o in config('CORS_ALLOWED_ORIGINS', default='').split(',') if o]
CORS_ALLOW_CREDENTIALS = True

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================
# Email y seguridad
# =====================
# Email Configuration (Development/Production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
PASSWORD_RESET_TIMEOUT = 86400  # 24 horas en segundos para expiración del token

# Security recommendations (para cuando DEBUG=False)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
CSRF_TRUSTED_ORIGINS = [o for o in config('CSRF_TRUSTED_ORIGINS', default='').split(',') if o]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True