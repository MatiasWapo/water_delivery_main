# =============================================
# FORMULARIOS PARA LA APLICACIÓN DE CLIENTES
# =============================================
# Este archivo contiene los formularios personalizados para la gestión
# de clientes, asegurando que todos los campos se procesen correctamente.

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
import re
from .models import Cliente, Pago

class ClienteForm(forms.ModelForm):
    """
    Formulario personalizado para crear y editar clientes.
    Incluye validación específica para todos los campos.
    """
    
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'direccion', 'telefono', 'precio_botellon']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent transition-all duration-200',
                'placeholder': 'Nombre del cliente',
                'maxlength': '50',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
                'title': 'Solo letras y espacios permitidos'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent transition-all duration-200',
                'placeholder': 'Apellido del cliente',
                'maxlength': '50',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
                'title': 'Solo letras y espacios permitidos'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent transition-all duration-200 resize-none',
                'rows': 3,
                'placeholder': 'Dirección completa del cliente',
                'maxlength': '200'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-agua-blue focus:border-transparent transition-all duration-200',
                'placeholder': 'Teléfono de contacto',
                'maxlength': '13',
                'pattern': '[0-9+\-\s()]+',
                'title': 'Solo números, espacios, guiones, paréntesis y + permitidos'
            }),
            'precio_botellon': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200',
                'step': '0.5',
                'min': '0',
                'max': '999.99',
                'placeholder': '2.50'
            })
        }

    def clean_nombre(self):
        """
        Validación para el campo nombre.
        - Solo permite letras y espacios
        - Mínimo 2 caracteres
        - Máximo 50 caracteres
        """
        nombre = self.cleaned_data.get('nombre')
        
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        
        # Remover espacios extra
        nombre = nombre.strip()
        
        if len(nombre) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        
        if len(nombre) > 50:
            raise ValidationError('El nombre no puede tener más de 50 caracteres.')
        
        # Validar que solo contenga letras y espacios
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise ValidationError('El nombre solo puede contener letras y espacios.')
        
        # Capitalizar primera letra de cada palabra
        nombre = nombre.title()
        
        return nombre

    def clean_apellido(self):
        """
        Validación para el campo apellido.
        - Solo permite letras y espacios
        - Mínimo 2 caracteres
        - Máximo 50 caracteres
        """
        apellido = self.cleaned_data.get('apellido')
        
        if not apellido:
            raise ValidationError('El apellido es obligatorio.')
        
        # Remover espacios extra
        apellido = apellido.strip()
        
        if len(apellido) < 2:
            raise ValidationError('El apellido debe tener al menos 2 caracteres.')
        
        if len(apellido) > 50:
            raise ValidationError('El apellido no puede tener más de 50 caracteres.')
        
        # Validar que solo contenga letras y espacios
        if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise ValidationError('El apellido solo puede contener letras y espacios.')
        
        # Capitalizar primera letra de cada palabra
        apellido = apellido.title()
        
        return apellido

    def clean_direccion(self):
        """
        Validación para el campo dirección.
        - Mínimo 10 caracteres
        - Máximo 200 caracteres
        """
        direccion = self.cleaned_data.get('direccion')
        
        if not direccion:
            raise ValidationError('La dirección es obligatoria.')
        
        # Remover espacios extra
        direccion = direccion.strip()
        
        if len(direccion) < 10:
            raise ValidationError('La dirección debe tener al menos 10 caracteres.')
        
        if len(direccion) > 200:
            raise ValidationError('La dirección no puede tener más de 200 caracteres.')
        
        return direccion

    def clean_telefono(self):
        """
        Validación para el campo teléfono.
        - Solo números, espacios, guiones, paréntesis y +
        - Mínimo 7 dígitos
        - Máximo 13 caracteres
        """
        telefono = self.cleaned_data.get('telefono')
        
        if not telefono:
            return telefono  # Teléfono es opcional
        
        # Remover espacios extra
        telefono = telefono.strip()
        
        if len(telefono) > 13:
            raise ValidationError('El teléfono no puede tener más de 13 caracteres.')
        
        # Validar formato permitido
        if not re.match(r'^[0-9+\-\s()]+$', telefono):
            raise ValidationError('El teléfono solo puede contener números, espacios, guiones, paréntesis y +.')
        
        # Contar solo dígitos
        digitos = re.findall(r'\d', telefono)
        if len(digitos) < 7:
            raise ValidationError('El teléfono debe tener al menos 7 dígitos.')
        
        if len(digitos) > 11:
            raise ValidationError('El teléfono no puede tener más de 11 dígitos.')
        
        return telefono

    def clean_precio_botellon(self):
        """
        Validación personalizada para el campo precio_botellon.
        Asegura que el valor sea válido y se procese correctamente.
        """
        precio = self.cleaned_data.get('precio_botellon')
        
        # Log para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] clean_precio_botellon - precio original: {precio} (tipo: {type(precio)})")
        
        # Si el precio es None o vacío, usar el valor por defecto
        if precio is None or precio == '':
            precio = Decimal('2.50')
            logger.info(f"[DEBUG] Precio vacío, usando valor por defecto: {precio}")
        
        # Convertir a Decimal si es necesario
        if not isinstance(precio, Decimal):
            try:
                precio = Decimal(str(precio))
                logger.info(f"[DEBUG] Precio convertido a Decimal: {precio}")
            except (ValueError, TypeError) as e:
                logger.error(f"[DEBUG] Error convirtiendo precio: {e}")
                raise ValidationError('El precio debe ser un número válido.')
        
        # Validar que el precio sea positivo
        if precio < 0:
            raise ValidationError('El precio no puede ser negativo.')
        
        # Validar que el precio no sea muy alto
        if precio > 999.99:
            raise ValidationError('El precio no puede ser mayor a $999.99.')
        
        # Validar que el precio tenga máximo 2 decimales
        if precio.as_tuple().exponent < -2:
            raise ValidationError('El precio puede tener máximo 2 decimales.')

        return precio


class PagoForm(forms.ModelForm):
    """Formulario para registrar o editar pagos de clientes."""

    class Meta:
        model = Pago
        fields = ['monto', 'observaciones']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'px-3 py-2 border rounded w-full',
                'step': '0.5',
                'min': '0.5',
                'placeholder': 'Monto ($)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'px-3 py-2 border rounded w-full resize-none',
                'rows': 3,
                'placeholder': 'Observaciones (opcional)'
            })
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is None:
            raise ValidationError('El monto es obligatorio.')
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        return monto


class ClienteEditForm(ClienteForm):
    """
    Formulario para editar clientes que incluye el campo activo.
    """
    
    class Meta(ClienteForm.Meta):
        fields = ['nombre', 'apellido', 'direccion', 'telefono', 'precio_botellon', 'activo']
        widgets = {
            **ClienteForm.Meta.widgets,
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valor por defecto para precio_botellon solo para nuevos clientes
        if not self.instance.pk:  # Solo para nuevos clientes
            self.fields['precio_botellon'].initial = Decimal('2.50')
        elif self.instance.pk and self.instance.precio_botellon:
            # Para clientes existentes, asegurar que el campo tenga el valor de la instancia
            # Convertir Decimal a float para que se muestre correctamente en el input number
            precio_value = float(self.instance.precio_botellon)
            self.fields['precio_botellon'].initial = precio_value
            # También establecerlo en self.initial para asegurar que se use
            self.initial['precio_botellon'] = precio_value
    
    def clean(self):
        """
        Validación general del formulario.
        """
        cleaned_data = super().clean()
        
        # Log para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DEBUG] clean() - datos limpios: {cleaned_data}")
        
        # Asegurarse de que el precio_botellon sea un número válido
        precio_botellon = cleaned_data.get('precio_botellon')
        if precio_botellon is not None:
            try:
                precio = float(precio_botellon)
                if precio < 0:
                    self.add_error('precio_botellon', 'El precio no puede ser negativo')
                # Asegurar que el precio tenga máximo 2 decimales
                if round(precio * 100) % 5 != 0:
                    self.add_error('precio_botellon', 'El precio debe ser múltiplo de 0.05')
            except (TypeError, ValueError):
                self.add_error('precio_botellon', 'Ingrese un precio válido')
        
        return cleaned_data
        
    def clean_precio_botellon(self):
        """Validación específica para el campo precio_botellon."""
        precio = self.cleaned_data.get('precio_botellon')
        if precio is not None:
            try:
                precio = float(precio)
                if precio < 0:
                    raise forms.ValidationError('El precio no puede ser negativo')
                return round(precio, 2)  # Asegurar 2 decimales
            except (TypeError, ValueError):
                raise forms.ValidationError('Ingrese un precio válido')
        return precio
        
        return cleaned_data 