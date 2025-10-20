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
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================
# Seguridad y rutas
# =====================
# SECRET_KEY, DEBUG, ALLOWED_HOSTS
# Security settings (¡OJO! Cambiar en producción)
SECRET_KEY = 'django-insecure-a!d5f&34%4n*2^4c*&6^0v2d=*c0x)$j-o#mvde^7odl4p2mi-'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Para desarrollo local

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
# URLs que no requieren autenticación de dispositivo
LOGIN_EXEMPT_URLS = [
    '/',
    '/usuarios/login/',
    '/usuarios/register/',
    '/usuarios/recuperar/',
    '/usuarios/resetear/',
    '/admin/',
    '/static/',
    '/media/',
]

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
]

# Middleware para desarrollo local
if DEBUG:
    # Deshabilitar restricciones de dispositivo en desarrollo
    MIDDLEWARE = [m for m in MIDDLEWARE if m != 'usuarios.middleware.DeviceDBMiddleware']
else:
    # En producción, mantener solo las restricciones necesarias
    MIDDLEWARE.append('water_delivery.security.IPRestrictionMiddleware')

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

# Configuración de base de datos PostgreSQL local
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
# Configuración de Email
# =====================
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'matiasmartimez15@gmail.com'
EMAIL_HOST_PASSWORD = 'matias123'  # Considera usar una contraseña de aplicación para mayor seguridad
DEFAULT_FROM_EMAIL = 'matiasmartimez15@gmail.com'

# Configuración de seguridad adicional para Gmail
# Asegúrate de que tu cuenta de Google permita el acceso de aplicaciones menos seguras
# o mejor aún, configura una contraseña de aplicación en tu cuenta de Google

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
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

# Security settings for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CSRF_TRUSTED_ORIGINS = []
SECURE_PROXY_SSL_HEADER = None
USE_X_FORWARDED_HOST = False