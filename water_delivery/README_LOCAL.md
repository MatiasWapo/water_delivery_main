# Configuración para Desarrollo Local

## Pasos para configurar el entorno local

### 1. Crear archivo `.env`

Copia el archivo `env.example` y renómbralo a `.env` en la misma carpeta (`water_delivery/`):

```bash
# En Windows (PowerShell)
Copy-Item env.example .env

# En Linux/Mac
cp env.example .env
```

### 2. Editar el archivo `.env`

Abre el archivo `.env` y configura los siguientes valores para desarrollo local:

```env
# Configuración para desarrollo local
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos local (ajusta según tu configuración)
DB_NAME=water_delivery_db
DB_USER=postgres
DB_PASSWORD=tu_password_local
DB_HOST=127.0.0.1
DB_PORT=5432

# Archivos estáticos y media (opcional - se usarán rutas relativas automáticamente)
STATIC_ROOT=staticfiles
MEDIA_ROOT=media
```

### 3. Ejecutar el proyecto

Una vez configurado el `.env`, ejecuta el proyecto normalmente:

```bash
python manage.py runserver
```

Django leerá automáticamente las variables del archivo `.env`.

## Notas importantes

- El archivo `.env` **NO** se sube al repositorio (está en `.gitignore`)
- Si no existe el archivo `.env`, Django usará los valores por defecto de producción
- Para producción, configura las variables de entorno directamente en el servidor o usa el archivo `.env` en el servidor

## Variables disponibles

- `DEBUG`: True para desarrollo, False para producción
- `ALLOWED_HOSTS`: Lista de hosts permitidos separados por coma
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Configuración de base de datos
- `STATIC_ROOT`, `MEDIA_ROOT`: Rutas para archivos estáticos y media (opcional)

