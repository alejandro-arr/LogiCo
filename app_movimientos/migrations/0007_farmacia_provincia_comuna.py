from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0006_movimiento_anulado_por_movimiento_fecha_anulacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmacia',
            name='provincia',
            field=models.CharField(default='', max_length=100, verbose_name='Provincia'),
        ),
        migrations.AddField(
            model_name='farmacia',
            name='comuna',
            field=models.CharField(default='', max_length=100, verbose_name='Comuna'),
        ),
    ]
