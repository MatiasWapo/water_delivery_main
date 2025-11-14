from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0005_configuracionrastreo_ubicacioncamion"),
    ]

    operations = [
        migrations.AddField(
            model_name="despacho",
            name="cancelado",
            field=models.BooleanField(default=False),
        ),
    ]
