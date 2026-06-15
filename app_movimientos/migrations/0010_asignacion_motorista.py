import django.db.models.deletion
from django.db import migrations, models


def migrar_ultimas_asignaciones(apps, schema_editor):
    AsignacionMotorista = apps.get_model('app_movimientos', 'AsignacionMotorista')
    AsignacionTurno = apps.get_model('app_movimientos', 'AsignacionTurno')

    motoristas_migrados = set()
    turnos = AsignacionTurno.objects.order_by(
        'motorista_id',
        '-fecha',
        '-id',
    )
    for turno in turnos:
        if turno.motorista_id in motoristas_migrados:
            continue
        AsignacionMotorista.objects.create(
            motorista_id=turno.motorista_id,
            farmacia_id=turno.farmacia_id,
            observaciones='Asignación migrada desde el último turno registrado.',
        )
        motoristas_migrados.add(turno.motorista_id)


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0009_catalogo_marcas_modelos_moto'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsignacionMotorista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de asignación')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('farmacia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='motoristas_asignados', to='app_movimientos.farmacia', verbose_name='Farmacia')),
                ('motorista', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='asignacion_farmacia', to='app_movimientos.motorista', verbose_name='Motorista')),
            ],
            options={
                'verbose_name': 'Asignación de motorista',
                'verbose_name_plural': 'Asignaciones',
                'ordering': ['farmacia__nombre_local', 'motorista__nombre_completo'],
            },
        ),
        migrations.RunPython(migrar_ultimas_asignaciones, migrations.RunPython.noop),
    ]
