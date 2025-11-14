from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0006_remove_usuario_pregunta_1_remove_usuario_pregunta_2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='token_recuperacion_fecha',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]