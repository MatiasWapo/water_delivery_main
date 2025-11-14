#!/bin/bash
# =============================================
# SCRIPT DE DESPLIEGUE PARA WATER DELIVERY
# =============================================
# Este script automatiza el proceso de despliegue
# Uso: ./deploy.sh

echo "🚀 Iniciando despliegue de Water Delivery..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio del proyecto."
    exit 1
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Verificar configuración
echo "✅ Verificando configuración..."
python manage.py check --deploy

echo "🎉 ¡Despliegue completado exitosamente!"
echo "📝 Recuerda configurar las variables de entorno en tu hosting." 