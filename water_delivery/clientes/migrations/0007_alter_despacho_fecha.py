from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0006_despacho_cancelado"),
    ]

    operations = [
        migrations.AlterField(
            model_name="despacho",
            name="fecha",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
