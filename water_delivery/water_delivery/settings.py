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
SECRET_KEY = config('SECRET_KEY', default='django-insecure-a!d5f&34%4n*2^4c*&6^0v2d=*c0x)$j-o#mvde^7odl4p2mi-')
DEBUG = config('DEBUG', default=True, cast=bool)  # True por defecto para desarrollo local

# ALLOWED_HOSTS puede ser sobrescrito desde .env o usar valores por defecto
ALLOWED_HOSTS_STR = config('ALLOWED_HOSTS', default='')
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_STR.split(',') if h.strip()]
else:
    # Valores por defecto para producción
    ALLOWED_HOSTS = [
        'matiaserver.click',
        'www.matiaserver.click',
        'inversioneslos2ramirez.matiaserver.click',
        '84.247.168.85',
        'localhost',
        '127.0.0.1',
    ]

# Configuración de seguridad CSRF
# En desarrollo (DEBUG=True), desactivar cookies seguras para permitir HTTP
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool)

# CSRF_TRUSTED_ORIGINS puede ser sobrescrito desde .env o usar valores por defecto
CSRF_TRUSTED_ORIGINS_STR = config('CSRF_TRUSTED_ORIGINS', default='')
if CSRF_TRUSTED_ORIGINS_STR:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in CSRF_TRUSTED_ORIGINS_STR.split(',') if o.strip()]
else:
    if DEBUG:
        # En desarrollo, permitir localhost con HTTP
        CSRF_TRUSTED_ORIGINS = [
            'http://localhost:8000',
            'http://127.0.0.1:8000',
            'http://localhost',
            'http://127.0.0.1',
        ]
    else:
        # Valores por defecto para producción
        CSRF_TRUSTED_ORIGINS = [
            'https://matiaserver.click',
            'https://www.matiaserver.click',
            'https://inversioneslos2ramirez.matiaserver.click',
            'https://84.247.168.85',
        ]

# Configuración de seguridad de sesiones
# En desarrollo (DEBUG=True), desactivar cookies seguras para permitir HTTP
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)

# Configuración SSL y seguridad adicional
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
USE_X_FORWARDED_HOST = True

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
    # Middleware de control por dispositivo deshabilitado
    # 'usuarios.middleware.DeviceDBMiddleware',
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

def _is_valid_database_url(url: str) -> bool:
    """Valida que la URL de base de datos sea válida y no sea un valor de ejemplo"""
    if not url:
        return False
    # Palabras que indican que es un valor de ejemplo
    example_keywords = ['usuario', 'contraseña', 'password', 'host', 'puerto', 'port', 'nombre_db', 'database']
    url_lower = url.lower()
    # Si contiene palabras de ejemplo, no es válida
    if any(keyword in url_lower for keyword in example_keywords):
        return False
    # Intentar parsear la URL para verificar que sea válida
    try:
        parsed = urlparse(url)
        # Debe tener scheme y netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        # Si tiene puerto, debe ser un número
        if ':' in parsed.netloc:
            host, port = parsed.netloc.rsplit(':', 1)
            try:
                int(port)
            except ValueError:
                return False
        return True
    except Exception:
        return False

# Configuración de la base de datos
# Si hay DATABASE_URL válida, úsala; si no, usa configuración por defecto
if DATABASE_URL and _is_valid_database_url(DATABASE_URL):
    DATABASES = {
        'default': dj_database_url.config(
            default=_ensure_sslmode(DATABASE_URL),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # En desarrollo (DEBUG=True), intentar usar PostgreSQL primero
    # Para forzar SQLite, configurar USE_SQLITE=True en .env
    USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)
    USE_POSTGRES = config('USE_POSTGRES', default=True, cast=bool)  # PostgreSQL por defecto
    
    if DEBUG and USE_SQLITE:
        # SQLite para desarrollo local (no requiere servidor de base de datos)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        # Configuración PostgreSQL (puede ser sobrescrita desde .env)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='water_delivery_db'),
                'USER': config('DB_USER', default='postgres'),
                'PASSWORD': config('DB_PASSWORD', default='matias123'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),  # Puerto correcto para PostgreSQL 18
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
# STATIC_ROOT puede ser sobrescrito desde .env, si no usa ruta por defecto según DEBUG
STATIC_ROOT = config('STATIC_ROOT', default=None)
if STATIC_ROOT is None:
    if DEBUG:
        # En desarrollo local, usa una carpeta relativa al proyecto
        STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    else:
        # En producción, usa la ruta absoluta
        STATIC_ROOT = '/opt/water_delivery_main/static/'

# Media files
MEDIA_URL = '/media/'
# MEDIA_ROOT puede ser sobrescrito desde .env, si no usa ruta por defecto según DEBUG
MEDIA_ROOT = config('MEDIA_ROOT', default=None)
if MEDIA_ROOT is None:
    if DEBUG:
        # En desarrollo local, usa una carpeta relativa al proyecto
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    else:
        # En producción, usa la ruta absoluta
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

# Security recommendations adicionales (pueden ser sobrescritas desde .env)
# Estas configuraciones ya están definidas arriba en la sección de seguridad