# =============================================
# COMANDO DE PRUEBA PARA VERIFICAR PRECIOS DE CLIENTES
# =============================================
# Este comando permite probar la creación de clientes con diferentes
# precios de botellón para verificar que se guarden correctamente.

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba la creación de clientes con diferentes precios de botellón'

    def add_arguments(self, parser):
        parser.add_argument(
            '--precio',
            type=float,
            default=3.0,
            help='Precio del botellón para el cliente de prueba'
        )

    def handle(self, *args, **options):
        precio = Decimal(str(options['precio']))
        
        # Crear un cliente de prueba
        cliente = Cliente.objects.create(
            nombre='Cliente',
            apellido='Prueba',
            direccion='Dirección de prueba',
            telefono='123456789',
            precio_botellon=precio
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cliente creado exitosamente:\n'
                f'  Nombre: {cliente.nombre} {cliente.apellido}\n'
                f'  Precio botellón: ${cliente.precio_botellon}\n'
                f'  ID: {cliente.id}'
            )
        )
        
        # Verificar que el precio se guardó correctamente
        cliente_refreshed = Cliente.objects.get(id=cliente.id)
        if cliente_refreshed.precio_botellon == precio:
            self.stdout.write(
                self.style.SUCCESS('✓ El precio se guardó correctamente en la base de datos')
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ Error: El precio no se guardó correctamente. '
                    f'Esperado: {precio}, Obtenido: {cliente_refreshed.precio_botellon}'
                )
            )
        
        # Limpiar el cliente de prueba
        cliente.delete()
        self.stdout.write('Cliente de prueba eliminado.') 