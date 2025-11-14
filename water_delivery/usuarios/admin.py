# =============================================
# CONFIGURACIÓN DEL ADMINISTRADOR DE USUARIOS
# =============================================
# Este archivo registra el modelo de usuario personalizado en el panel de administración
# de Django y personaliza su visualización, filtros y campos adicionales.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Device

class UsuarioAdmin(UserAdmin):
    # Lista de campos a mostrar en la tabla principal
    list_display = ('username', 'email', 'mostrar_tipo_usuario', 'is_active', 'is_superuser', 'camion_asignado')
    list_filter = ('tipo_usuario', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'tipo_usuario')
    ordering = ('-is_superuser', '-is_active', 'username')
    
    # Campos para la edición detallada
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {
            'fields': (
                'tipo_usuario',
                'telefono',
                'direccion',
                'camion_asignado',
            ),
        }),
    )

    @admin.display(description='Tipo Usuario')
    def mostrar_tipo_usuario(self, obj):
        if obj.is_superuser:
            return 'Superusuario'
        return obj.get_tipo_usuario_display()

# Registro del modelo Usuario en el admin
admin.site.register(Usuario, UsuarioAdmin)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'last_seen', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'token')
    readonly_fields = ('token', 'last_seen', 'created_at')