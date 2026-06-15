import django.db.models.deletion
from django.db import migrations, models


def copiar_farmacia_desde_turno(apps, schema_editor):
    Movimiento = apps.get_model('app_movimientos', 'Movimiento')
    for movimiento in Movimiento.objects.select_related('asignacion_turno'):
        movimiento.farmacia_origen_id = movimiento.asignacion_turno.farmacia_id
        movimiento.save(update_fields=['farmacia_origen'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0011_alter_usuariosistema_rol'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='farmacia_origen',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos_origen',
                to='app_movimientos.farmacia',
                verbose_name='Origen del movimiento',
            ),
        ),
        migrations.RunPython(copiar_farmacia_desde_turno, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='movimiento',
            name='farmacia_origen',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos_origen',
                to='app_movimientos.farmacia',
                verbose_name='Origen del movimiento',
            ),
        ),
        migrations.AlterField(
            model_name='movimiento',
            name='asignacion_turno',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos',
                to='app_movimientos.asignacionturno',
                verbose_name='Turno operativo',
            ),
        ),
    ]
