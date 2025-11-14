# =============================================
# MODELOS DE CLIENTE, DESPACHO Y PAGO
# =============================================
# Este archivo define las estructuras de datos principales para la app de clientes:
# Cliente: información y saldo del cliente.
# Despacho: registro de entregas de botellones.
# Pago: registro de abonos realizados por el cliente.

from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    """
    Modelo que representa a un cliente de la empresa.
    Guarda datos personales, dirección, teléfono, estado y saldo.
    """
    nombre = models.CharField(max_length=100)  # Nombre del cliente
    apellido = models.CharField(max_length=100)  # Apellido del cliente
    direccion = models.TextField()  # Dirección completa
    telefono = models.CharField(max_length=20)  # Teléfono de contacto
    activo = models.BooleanField(default=True)  # Si el cliente está activo
    debe_total = models.IntegerField(default=0)  # Deuda total acumulada
    precio_botellon = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)  # Precio por botellón
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Saldo actual del cliente
    
    def __str__(self):
        """Representación legible del cliente"""
        return f"{self.nombre} {self.apellido}"

class Despacho(models.Model):
    """
    Modelo que representa un despacho (entrega) de botellones a un cliente.
    Guarda cantidad, fecha, notas, precio y estado de entrega.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)  # Cliente asociado
    fecha = models.DateTimeField(default=timezone.now)  # Fecha y hora del despacho
    cantidad_botellones = models.IntegerField()  # Cantidad de botellones entregados
    entregado = models.BooleanField(default=False)  # Si el despacho fue entregado
    cancelado = models.BooleanField(default=False)  # Si el despacho fue cancelado y descontado
    notas = models.TextField(blank=True, null=True)  # Notas adicionales
    precio_unitario = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)  # Precio por botellón
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total del despacho
    
    def __str__(self):
        """Representación legible del despacho"""
        return f"Despacho a {self.cliente} - {self.cantidad_botellones} botellones"

class Pago(models.Model):
    """
    Modelo que representa un pago realizado por un cliente.
    Guarda monto, fecha, observaciones y cliente asociado.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pagos')  # Cliente que paga
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha y hora del pago
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto del pago
    observaciones = models.TextField(blank=True, null=True)  # Observaciones adicionales
    def __str__(self):
        """Representación legible del pago"""
        return f"Pago de {self.monto} $ de {self.cliente} el {self.fecha.strftime('%d/%m/%Y')}"

class UbicacionCamion(models.Model):
    """
    Modelo para almacenar la ubicación del camión en tiempo real.
    Permite rastrear la posición del conductor durante las entregas.
    """
    conductor = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='ubicaciones')
    latitud = models.DecimalField(max_digits=10, decimal_places=8, help_text="Latitud de la ubicación")
    longitud = models.DecimalField(max_digits=11, decimal_places=8, help_text="Longitud de la ubicación")
    direccion = models.CharField(max_length=255, blank=True, help_text="Dirección aproximada de la ubicación")
    velocidad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Velocidad en km/h")
    bateria = models.IntegerField(null=True, blank=True, help_text="Porcentaje de batería del dispositivo")
    senal_gps = models.CharField(max_length=20, default='Buena', help_text="Calidad de la señal GPS")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Momento exacto de la ubicación")
    activo = models.BooleanField(default=True, help_text="Indica si esta ubicación está activa")
    
    class Meta:
        verbose_name = "Ubicación del Camión"
        verbose_name_plural = "Ubicaciones del Camión"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['conductor', '-timestamp']),
            models.Index(fields=['activo', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.conductor} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def coordenadas(self):
        """Retorna las coordenadas como diccionario."""
        return {
            'lat': float(self.latitud),
            'lng': float(self.longitud)
        }
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la ubicación."""
        from django.utils import timezone
        ahora = timezone.now()
        diferencia = ahora - self.timestamp
        minutos = int(diferencia.total_seconds() / 60)
        
        if minutos < 1:
            return "Hace menos de 1 minuto"
        elif minutos == 1:
            return "Hace 1 minuto"
        elif minutos < 60:
            return f"Hace {minutos} minutos"
        else:
            horas = minutos // 60
            return f"Hace {horas} hora{'s' if horas != 1 else ''}"

class ConfiguracionRastreo(models.Model):
    """
    Modelo para configurar el rastreo del camión.
    Permite personalizar la frecuencia de actualización y otros parámetros.
    """
    empresa = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='configuraciones_rastreo')
    conductor_asignado = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='rastreo_asignado', null=True, blank=True)
    frecuencia_actualizacion = models.IntegerField(default=60, help_text="Frecuencia de actualización en segundos")
    rastreo_activo = models.BooleanField(default=True, help_text="Indica si el rastreo está activo")
    radio_alertas = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, help_text="Radio en km para alertas de zona")
    notificaciones_email = models.BooleanField(default=True, help_text="Enviar notificaciones por email")
    notificaciones_push = models.BooleanField(default=True, help_text="Enviar notificaciones push")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Rastreo"
        verbose_name_plural = "Configuraciones de Rastreo"
        unique_together = ['empresa', 'conductor_asignado']
    
    def __str__(self):
        return f"Rastreo de {self.conductor_asignado} - {self.empresa}"
    
    @property
    def frecuencia_minutos(self):
        """Retorna la frecuencia en formato legible."""
        if self.frecuencia_actualizacion < 60:
            return f"{self.frecuencia_actualizacion} segundos"
        else:
            minutos = self.frecuencia_actualizacion // 60
            return f"{minutos} minuto{'s' if minutos != 1 else ''}"
