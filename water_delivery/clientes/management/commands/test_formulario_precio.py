# =============================================
# COMANDO DE PRUEBA PARA VERIFICAR EL FORMULARIO PERSONALIZADO
# =============================================
# Este comando prueba el formulario personalizado con diferentes precios
# para verificar que se procesen correctamente.

from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from clientes.forms import ClienteForm
from clientes.models import Cliente
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba el formulario personalizado con diferentes precios'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando prueba del formulario personalizado...')
        
        # Crear un usuario de prueba
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='admin',
                email='admin@test.com',
                password='admin123',
                tipo_usuario='empresa'
            )
        
        # Datos de prueba
        test_data = {
            'nombre': 'Cliente',
            'apellido': 'Prueba Formulario',
            'direccion': 'Dirección de prueba',
            'telefono': '123456789',
            'precio_botellon': '3.50'  # Precio personalizado
        }
        
        self.stdout.write(f'Datos de prueba: {test_data}')
        
        # Crear formulario con datos de prueba
        form = ClienteForm(data=test_data)
        
        if form.is_valid():
            self.stdout.write(
                self.style.SUCCESS('✓ El formulario es válido')
            )
            self.stdout.write(f'Datos limpios: {form.cleaned_data}')
            
            # Crear el cliente
            cliente = form.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cliente creado exitosamente:\n'
                    f'  Nombre: {cliente.nombre} {cliente.apellido}\n'
                    f'  Precio botellón: ${cliente.precio_botellon}\n'
                    f'  ID: {cliente.id}'
                )
            )
            
            # Verificar que el precio se guardó correctamente
            if cliente.precio_botellon == Decimal('3.50'):
                self.stdout.write(
                    self.style.SUCCESS('✓ El precio se guardó correctamente')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error: El precio no se guardó correctamente. '
                        f'Esperado: 3.50, Obtenido: {cliente.precio_botellon}'
                    )
                )
            
            # Limpiar el cliente de prueba
            cliente.delete()
            self.stdout.write('Cliente de prueba eliminado.')
            
        else:
            self.stdout.write(
                self.style.ERROR('✗ El formulario no es válido')
            )
            self.stdout.write(f'Errores: {form.errors}')
        
        self.stdout.write(
            self.style.SUCCESS('Prueba del formulario completada.')
        ) 