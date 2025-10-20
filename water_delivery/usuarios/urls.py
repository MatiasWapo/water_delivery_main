# =============================================
# RUTAS DE AUTENTICACIÓN Y RECUPERACIÓN DE USUARIOS
# =============================================
# Define las URLs para login, logout, registro, recuperación y reseteo de contraseña.

from django.urls import path
from .views import (
    CustomLoginView, 
    CustomLogoutView, 
    CustomRegisterView,
    RecuperacionEmailView,
    ResetearConTokenView,
    device_login,
    device_logout,
)
app_name = 'usuarios'

urlpatterns = [
    # Login de usuario
    path('login/', CustomLoginView.as_view(), name='login'),
    # Logout de usuario
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    # Registro de nuevo usuario
    path('register/', CustomRegisterView.as_view(), name='register'),
    # Recuperación de contraseña por email
    path('recuperar/', RecuperacionEmailView.as_view(), name='recuperar'),
    # Reseteo de contraseña con token enviado por email
    path('resetear/<str:token>/', ResetearConTokenView.as_view(), name='resetear_con_token'),
    # Login/logout de dispositivo (allowlist por DB)
    path('device/login/', device_login, name='device_login'),
    path('device/logout/', device_logout, name='device_logout'),
]