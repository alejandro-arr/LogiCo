from django.db import migrations, models
import app_movimientos.models


def asignar_codigos_existentes(apps, schema_editor):
    Movimiento = apps.get_model('app_movimientos', 'Movimiento')
    for movimiento in Movimiento.objects.order_by('id'):
        movimiento.codigo = f'MOV-{movimiento.id:06d}'
        movimiento.save(update_fields=['codigo'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0013_movimiento_motorista'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='codigo',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Código de movimiento'),
        ),
        migrations.AddField(
            model_name='movimiento',
            name='observaciones',
            field=models.TextField(blank=True, verbose_name='Observaciones'),
        ),
        migrations.RunPython(asignar_codigos_existentes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='movimiento',
            name='codigo',
            field=models.CharField(
                default=app_movimientos.models.generar_codigo_movimiento,
                max_length=20,
                unique=True,
                verbose_name='Código de movimiento',
            ),
        ),
    ]
