# Procfile raiz para Railway/Heroku
# Usa rutas relativas al repo
web: sh -c "python water_delivery/manage.py migrate && python water_delivery/manage.py collectstatic --noinput && gunicorn water_delivery.wsgi:application --bind 0.0.0.0:$PORT"
