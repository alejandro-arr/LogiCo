import django.db.models.deletion
from django.db import migrations, models


def copiar_motorista_desde_turno(apps, schema_editor):
    Movimiento = apps.get_model('app_movimientos', 'Movimiento')
    for movimiento in Movimiento.objects.filter(
        asignacion_turno__isnull=False,
    ).select_related('asignacion_turno'):
        movimiento.motorista_id = movimiento.asignacion_turno.motorista_id
        movimiento.save(update_fields=['motorista'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0012_movimiento_farmacia_origen'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='motorista',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos',
                to='app_movimientos.motorista',
                verbose_name='Motorista',
            ),
        ),
        migrations.RunPython(copiar_motorista_desde_turno, migrations.RunPython.noop),
    ]
