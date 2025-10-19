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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================
# Seguridad y rutas
# =====================
# SECRET_KEY, DEBUG, ALLOWED_HOSTS
# Security settings (¡OJO! Cambiar en producción)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-a!d5f&34%4n*2^4c*&6^0v2d=*c0x)$j-o#mvde^7odl4p2mi-')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,192.168.154.204').split(',')

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.LoginRequiredMiddleware',
]

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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "water_delivery_db",
        "USER": "postgres",
        "PASSWORD": "matias123",
        "HOST": "127.0.0.1",
        "PORT": "5432",
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
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================
# Email y seguridad
# =====================
# Email Configuration (Development)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'matiasmartimez15@gmail.com'  # Cambiar por tu email real
EMAIL_HOST_PASSWORD = 'cezh kyul uxeo nnij'  # Usar contraseña de aplicación
DEFAULT_FROM_EMAIL = 'matiasmartimez15@gmail.com'  # Debe coincidir con EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT = 86400  # 24 horas en segundos para expiración del token

# Security recommendations (para cuando DEBUG=False)
SESSION_COOKIE_SECURE = False  # Cambiar a True en producción
CSRF_COOKIE_SECURE = False     # Cambiar a True en producción
SECURE_SSL_REDIRECT = False    # Cambiar a True en producción