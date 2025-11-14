from django.db import migrations

def forwards_func(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    for usuario in Usuario.objects.all():
        # Si no tiene preguntas configuradas, asigna las predeterminadas
        if not hasattr(usuario, 'pregunta_seguridad_1'):
            usuario.pregunta_seguridad_1 = 'ciudad'
            usuario.pregunta_seguridad_2 = 'comida'
            usuario.save()

class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0003_alter_usuario_options_alter_usuario_camion_asignado_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]