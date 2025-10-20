# =============================================
# FORMULARIOS DE AUTENTICACIÓN Y RECUPERACIÓN DE USUARIOS
# =============================================
# Este archivo contiene formularios para registro, login y recuperación de contraseña
# de usuarios del sistema Water Delivery. Incluye validaciones personalizadas y
# manejo de errores específicos para cada tipo de usuario.

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Usuario

class CustomLoginForm(AuthenticationForm):
    """
    Formulario personalizado para login con validaciones específicas.
    """
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent placeholder-gray-400 transition-all duration-200',
            'placeholder': 'Ingresa tu nombre de usuario'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent placeholder-gray-400 transition-all duration-200',
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        """
        Validación personalizada para el login.
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Intentar autenticar el usuario
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            if user is None:
                raise forms.ValidationError(
                    "Por favor, introduzca un nombre de usuario y clave correctos. "
                    "Observe que ambos campos pueden ser sensibles a mayúsculas."
                )
            elif not user.is_active:
                raise forms.ValidationError(
                    "Esta cuenta está desactivada. Contacta al administrador."
                )
        
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado para el registro de nuevos usuarios.
    Incluye validaciones de teléfono, dirección y tipo de usuario.
    """
    telefono = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,15}$',
                message="Formato de teléfono inválido. Use +584144770130 o 04144770130"
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 pl-12',
            'placeholder': 'Ej: +584144770130 o 04144770130'
        }),
        label='Teléfono'
    )
    
    direccion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 pl-12 resize-none',
            'placeholder': 'Ingresa tu dirección completa...',
            'rows': 3
        }),
        label='Dirección'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 pl-12',
            'placeholder': 'tu@ejemplo.com'
        }),
        label='Correo Electrónico'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password1', 'password2',
            'telefono', 'direccion', 'tipo_usuario'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.fields['username'].error_messages = {
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.',
            'max_length': 'El nombre de usuario no puede tener más de 150 caracteres.',
        }
        self.fields['email'].error_messages = {
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Por favor, ingresa un correo electrónico válido.',
            'unique': 'Este correo electrónico ya está registrado.',
        }
        self.fields['password1'].error_messages = {
            'required': 'La contraseña es obligatoria.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Debes confirmar tu contraseña.',
        }

    def clean_username(self):
        """
        Valida que el nombre de usuario no contenga caracteres especiales.
        """
        username = self.cleaned_data.get('username')
        if username:
            # Verificar que solo contenga letras, números y guiones bajos
            if not username.replace('_', '').replace('-', '').isalnum():
                raise forms.ValidationError(
                    'El nombre de usuario solo puede contener letras, números, guiones bajos (_) y guiones medios (-).'
                )
        return username

class RecuperacionForm(forms.Form):
    """
    Formulario para solicitar recuperación de cuenta por nombre de usuario.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message="El nombre de usuario solo puede contener letras, números, guiones bajos (_) y guiones medios (-)"
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        }),
        label='Nombre de usuario'
    )

class EmailForm(forms.Form):
    """
    Formulario para solicitar recuperación de cuenta por email.
    """
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'tu@ejemplo.com'
        })
    )
    
class ResetPasswordForm(forms.Form):
    """
    Formulario para restablecer la contraseña usando un token de recuperación.
    """
    nueva_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 pl-12',
            'placeholder': 'Ingresa tu nueva contraseña'
        }),
        validators=[
            MinLengthValidator(8, message="La contraseña debe tener al menos 8 caracteres"),
            RegexValidator(
                regex='^(?=.*[A-Za-z])(?=.*\d)',
                message="La contraseña debe contener letras y números"
            )
        ]
    )
    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 pl-12',
            'placeholder': 'Confirma tu nueva contraseña'
        })
    )

    def clean(self):
        """
        Valida que ambas contraseñas coincidan y que la nueva contraseña sea segura.
        """
        cleaned_data = super().clean()
        nueva_password = cleaned_data.get("nueva_password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if nueva_password and confirmar_password and nueva_password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

        try:
            validate_password(nueva_password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        return cleaned_data