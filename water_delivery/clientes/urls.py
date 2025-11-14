# =============================================
# RUTAS DE CLIENTES Y DESPACHOS
# =============================================
# Define las URLs para vistas de clientes, despachos, historial, pagos y APIs AJAX.

from django.urls import path
from .views import *

app_name = 'clientes'

urlpatterns = [
    # Dashboard principal (solo para usuarios logueados)
    path('', dashboard, name='dashboard'),
    # Lista de clientes
    path('lista/', ClienteListView.as_view(), name='lista_clientes'),
    # Crear nuevo cliente
    path('nuevo/', ClienteCreateView.as_view(), name='nuevo_cliente'),
    # Detalle de cliente
    path('<int:pk>/', ClienteDetailView.as_view(), name='detalle_cliente'),
    # Editar cliente
    path('editar/<int:pk>/', ClienteUpdateView.as_view(), name='editar_cliente'),
    # Nuevo despacho
    path('despacho/nuevo/', DespachoCreateView.as_view(), name='nuevo_despacho'),
    # Marcar despacho como entregado
    path('despacho/<int:pk>/entregado/', marcar_entregado, name='marcar_entregado'),
    # Marcar despacho como pendiente
    path('despacho/<int:pk>/pendiente/', marcar_pendiente, name='marcar_pendiente'),
    # Eliminar despacho
    path('despacho/<int:pk>/eliminar/', eliminar_despacho, name='eliminar_despacho'),
    # Habilitar/deshabilitar cliente
    path('toggle-status/<int:pk>/', toggle_cliente_status, name='toggle_cliente_status'),
    # Registrar pago de cliente
    path('registrar-pago/<int:cliente_id>/', registrar_pago, name='registrar_pago'),
    # Editar/eliminar pago
    path('pago/<int:pago_id>/editar/', editar_pago, name='editar_pago'),
    path('pago/<int:pago_id>/eliminar/', eliminar_pago, name='eliminar_pago'),
    # Dashboard de despachos
    path('dashboard-despachos/', dashboard_despachos, name='dashboard_despachos'),
    # Historial de despachos
    path('historial-despachos/', historial_despachos, name='historial_despachos'),
    # =====================
    # APIs para AJAX/JS
    # =====================
    # API: lista de clientes activos
    path('api/clientes/', api_clientes_activos, name='api_clientes'),
    # API: despachos de hoy
    path('api/despachos-hoy/', api_despachos_hoy, name='api_despachos_hoy'),
    # API: despachos recientes (últimos 10 días)
    path('api/despachos-recientes/', api_despachos_recientes, name='api_despachos_recientes'),
    # API: crear despacho
    path('api/crear-despacho/', api_crear_despacho, name='api_crear_despacho'),
    # API: crear cliente
    path('api/crear-cliente/', api_crear_cliente, name='api_crear_cliente'),
    # API: eliminar despacho
    path('api/eliminar-despacho/<int:despacho_id>/', api_eliminar_despacho, name='api_eliminar_despacho'),
    # API: marcar despacho como entregado
    path('api/marcar-entregado/<int:despacho_id>/', api_marcar_entregado, name='api_marcar_entregado'),
    # API: marcar despacho como cancelado descontado
    path('api/marcar-cancelado/<int:despacho_id>/', api_marcar_cancelado, name='api_marcar_cancelado'),
    # API: guardar ubicación del camión
    path('api/guardar-ubicacion/', api_guardar_ubicacion, name='api_guardar_ubicacion'),
    # API: información del conductor
    path('api/conductor-info/', api_conductor_info, name='api_conductor_info'),
    # Ruta del camión en tiempo real
    path('ruta/', ruta_camion, name='ruta_camion'),
]