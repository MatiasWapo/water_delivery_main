# =============================================
# COMANDO DE PRUEBA PARA VERIFICAR EL PROBLEMA DEL PRECIO
# =============================================
# Este comando simula el envío de un formulario con precio personalizado
# para verificar que se guarde correctamente.

from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba la creación de clientes con precio personalizado'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando prueba de precio personalizado...')
        
        # Crear un usuario de prueba (empresa)
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='admin',
                email='admin@test.com',
                password='admin123',
                tipo_usuario='empresa'
            )
        
        # Crear cliente directamente con precio personalizado
        cliente = Cliente.objects.create(
            nombre='Cliente',
            apellido='Prueba Precio',
            direccion='Dirección de prueba',
            telefono='123456789',
            precio_botellon=Decimal('3.50')
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cliente creado directamente:\n'
                f'  Nombre: {cliente.nombre} {cliente.apellido}\n'
                f'  Precio botellón: ${cliente.precio_botellon}\n'
                f'  ID: {cliente.id}'
            )
        )
        
        # Verificar que el precio se guardó correctamente
        cliente_refreshed = Cliente.objects.get(id=cliente.id)
        if cliente_refreshed.precio_botellon == Decimal('3.50'):
            self.stdout.write(
                self.style.SUCCESS('✓ El precio se guardó correctamente en la base de datos')
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Error: El precio no se guardó correctamente. '
                    f'Esperado: 3.50, Obtenido: {cliente_refreshed.precio_botellon}'
                )
            )
        
        # Limpiar el cliente de prueba
        cliente.delete()
        self.stdout.write('Cliente de prueba eliminado.')
        
        self.stdout.write(
            self.style.SUCCESS('Prueba completada. Si el precio se guardó correctamente, el problema está en el formulario web.')
        ) 