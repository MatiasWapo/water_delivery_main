# =============================================
# TESTS AUTOMATIZADOS PARA LA APP DE USUARIOS
# =============================================
# Este archivo contiene pruebas unitarias para la recuperación de contraseña
# y validación de usuarios del sistema.

from django.test import TestCase
from django.urls import reverse
from .models import Usuario

class UsuarioTests(TestCase):
    """
    Pruebas básicas para el modelo de usuario y funcionalidades principales.
    """
    def setUp(self):
        # Crea un usuario de prueba
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            tipo_usuario='conductor'
        )

    def test_crear_usuario(self):
        """
        Prueba que se puede crear un usuario correctamente.
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.tipo_usuario, 'conductor')
        self.assertTrue(self.user.is_active)

    def test_login_view(self):
        """
        Prueba que la vista de login funciona correctamente.
        """
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_view(self):
        """
        Prueba que la vista de registro funciona correctamente.
        """
        response = self.client.get(reverse('usuarios:register'))
        self.assertEqual(response.status_code, 200)

    def test_recuperacion_view(self):
        """
        Prueba que la vista de recuperación funciona correctamente.
        """
        response = self.client.get(reverse('usuarios:recuperar'))
        self.assertEqual(response.status_code, 200)