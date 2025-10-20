# =============================================
# VISTAS DE AUTENTICACIÓN Y RECUPERACIÓN DE USUARIOS
# =============================================
# Este archivo contiene las vistas para login, logout, registro y recuperación
# de contraseña de los usuarios del sistema Water Delivery. Incluye lógica para
# distinguir entre empresa y conductor, y manejo de tokens de recuperación.

from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomUserCreationForm, RecuperacionForm, EmailForm, ResetPasswordForm, CustomLoginForm
from .models import Usuario, Device

from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

import secrets
from django.conf import settings
from django.db import transaction, connection


DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class CustomLoginView(LoginView):
    """
    Vista personalizada de login.
    Redirige según el tipo de usuario (empresa o conductor) tras iniciar sesión.
    """
    template_name = 'usuarios/login.html'
    form_class = CustomLoginForm
    
    def get_success_url(self):
        """
        Determina la URL de redirección tras login exitoso.
        Si hay 'next', la usa; si no, redirige según el tipo de usuario.
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        # Redirigir según el tipo de usuario
        if hasattr(self.request.user, 'tipo_usuario'):
            if self.request.user.tipo_usuario == 'empresa':
                return reverse_lazy('clientes:lista_clientes')  # acceso total
            elif self.request.user.tipo_usuario == 'conductor':
                return reverse_lazy('clientes:nuevo_despacho')  # solo despachos
        return reverse_lazy('clientes:lista_clientes')

class CustomLogoutView(LogoutView):
    """
    Vista personalizada de logout.
    Redirige siempre a la página de login.
    """
    next_page = reverse_lazy('usuarios:login')

# =====================
# Login/Logout de Dispositivo (control por DB)
# =====================
def device_login(request):
    """
    Vista para ingresar el token de dispositivo y guardarlo en cookie segura.
    Si el token es válido y el dispositivo está activo, se permite el acceso.
    """
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('usuarios:login')

        if not token:
            return render(request, 'usuarios/device_login.html', {
                'error': 'Debes ingresar un token de dispositivo.',
                'next': next_url,
            })

        try:
            device = Device.objects.get(token=token, active=True)
        except Device.DoesNotExist:
            return render(request, 'usuarios/device_login.html', {
                'error': 'Token inválido o dispositivo desactivado.',
                'next': next_url,
            })

        response = redirect(next_url)
        # Cookie segura y httpOnly
        response.set_cookie(
            'DEVICE_TOKEN', token,
            max_age=60*60*24*30,  # 30 días
            secure=request.is_secure(),
            httponly=True,
            samesite='Strict',
        )
        return response

    # GET
    next_url = request.GET.get('next') or reverse('usuarios:login')
    return render(request, 'usuarios/device_login.html', {'next': next_url})


def device_logout(request):
    """
    Elimina la cookie de token de dispositivo y redirige al login.
    """
    response = redirect(reverse('usuarios:login'))
    response.delete_cookie('DEVICE_TOKEN')
    return response

class CustomRegisterView(CreateView):
    """
    Vista de registro de nuevos usuarios.
    Muestra mensajes de éxito o error según el resultado del formulario.
    """
    form_class = CustomUserCreationForm
    template_name = 'usuarios/register.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        """
        Si el formulario es válido, registra el usuario y muestra mensaje de éxito.
        """
        response = super().form_valid(form)
        messages.success(self.request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
        return response

    def form_invalid(self, form):
        """
        Si el formulario es inválido, muestra mensajes de error detallados.
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request,
                    f"Error en {form.fields[field].label}: {error}"
                )
        return super().form_invalid(form)

class RecuperacionEmailView(FormView):
    """
    Vista para solicitar recuperación de contraseña por email.
    Envía un enlace de recuperación si el email existe en el sistema.
    """
    template_name = 'usuarios/recuperacion_email.html'
    form_class = EmailForm
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        """
        Si el email existe, genera token y envía correo de recuperación.
        """
        email = form.cleaned_data['email']
        try:
            usuario = Usuario.objects.get(email=email)
            
            token = secrets.token_urlsafe(32)
            usuario.token_recuperacion = token
            usuario.token_recuperacion_fecha = timezone.now()
            usuario.save()
            
            # Construye la URL de reseteo
            reset_url = self.request.build_absolute_uri(
                reverse('usuarios:resetear_con_token', kwargs={'token': token})
            )
            
            send_mail(
                'Recuperación de contraseña - Water Delivery',
                f'''Hola {usuario.username},
                
Para restablecer tu contraseña, por favor haz clic en el siguiente enlace:
{reset_url}

Este enlace expirará en 24 horas.

Si no solicitaste este cambio, ignora este mensaje.

Atentamente,
El equipo de Water Delivery''',
                DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            
            messages.success(self.request, 'Se ha enviado un enlace de recuperación a tu correo electrónico.')
            return super().form_valid(form)
            
        except Usuario.DoesNotExist:
            messages.error(self.request, 'No existe una cuenta asociada a este correo electrónico.')
            return self.form_invalid(form)

class ResetearConTokenView(FormView):
    """
    Vista para restablecer la contraseña usando un token enviado por email.
    Valida el token y permite cambiar la contraseña si es válido.
    """
    template_name = 'usuarios/resetear_con_token.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        """
        Valida el token de recuperación antes de mostrar el formulario.
        """
        token = kwargs.get('token')
        try:
            self.usuario = Usuario.objects.get(
                token_recuperacion=token,
                token_recuperacion_fecha__gte=timezone.now()-timedelta(hours=24)
            )
            return super().dispatch(request, *args, **kwargs)
        except Usuario.DoesNotExist:
            messages.error(request, 'El enlace de recuperación no es válido o ha expirado.')
            return redirect('usuarios:recuperar')

    def get_context_data(self, **kwargs):
        """
        Agrega el usuario al contexto para mostrar información en el template.
        """
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.usuario
        return context

    def form_valid(self, form):
        """
        Si el formulario es válido, actualiza la contraseña y elimina el token.
        """
        nueva_password = form.cleaned_data['nueva_password']
        try:
            with transaction.atomic():
                self.usuario.set_password(nueva_password)
                self.usuario.token_recuperacion = None
                self.usuario.token_recuperacion_fecha = None
                self.usuario.save()
                messages.success(self.request, '¡Contraseña actualizada correctamente!')
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Error crítico: {str(e)}')
            return self.form_invalid(form)