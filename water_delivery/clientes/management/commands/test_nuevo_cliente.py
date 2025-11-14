# =============================================
# COMANDO DE PRUEBA PARA VERIFICAR NUEVO CLIENTE
# =============================================
# Este comando prueba la creación de clientes con diferentes precios
# para verificar que el formulario funcione correctamente.

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba la creación de clientes con diferentes precios'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando prueba de nuevo cliente...')
        
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
        
        # Probar diferentes precios
        precios_prueba = ['2.50', '3.00', '3.50', '4.00']
        
        for precio in precios_prueba:
            self.stdout.write(f'\nProbando precio: ${precio}')
            
            # Crear cliente con precio específico
            cliente = Cliente.objects.create(
                nombre=f'Cliente Prueba {precio}',
                apellido='Test',
                direccion='Dirección de prueba',
                telefono='123456789',
                precio_botellon=Decimal(precio)
            )
            
            # Verificar que se guardó correctamente
            cliente_refreshed = Cliente.objects.get(id=cliente.id)
            
            if cliente_refreshed.precio_botellon == Decimal(precio):
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Precio ${precio} guardado correctamente')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error: Precio ${precio} no se guardó correctamente')
                )
            
            # Limpiar cliente de prueba
            cliente.delete()
        
        self.stdout.write(
            self.style.SUCCESS('\nPrueba completada. Si todos los precios se guardaron correctamente, el problema está en el formulario web.')
        ) 