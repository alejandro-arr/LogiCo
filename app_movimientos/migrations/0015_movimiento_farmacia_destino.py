import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0014_movimiento_codigo_observaciones'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='farmacia_destino',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos_destino',
                to='app_movimientos.farmacia',
                verbose_name='Farmacia de destino',
            ),
        ),
    ]
