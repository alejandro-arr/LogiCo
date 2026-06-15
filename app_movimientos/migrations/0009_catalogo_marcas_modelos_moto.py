import django.db.models.deletion
from django.db import migrations, models


CATALOGO_INICIAL = {
    'Bajaj': [
        'Boxer 150',
        'Dominar 250',
        'Dominar 400',
        'Pulsar NS160',
        'Pulsar NS200',
    ],
    'BMW': [
        'G 310 GS',
        'G 310 R',
        'F 750 GS',
        'F 850 GS',
    ],
    'CFMoto': [
        '250 NK',
        '300 NK',
        '450 MT',
        '650 MT',
    ],
    'Honda': [
        'NAVI',
        'DIO',
        'Elite 125',
        'CB125F',
        'CB190R',
        'CB300F',
        'XR150L',
        'XR190L',
    ],
    'Kawasaki': [
        'Ninja 400',
        'Versys-X 300',
        'Z400',
        'Z650',
    ],
    'KTM': [
        'Duke 200',
        'Duke 250',
        'Duke 390',
        'Adventure 390',
    ],
    'Royal Enfield': [
        'Classic 350',
        'Himalayan 450',
        'Hunter 350',
        'Meteor 350',
    ],
    'Suzuki': [
        'Burgman Street 125',
        'GIXXER 150 FI',
        'GIXXER 250 FI',
        'GN125',
        'V-STROM 250 SX',
    ],
    'TVS': [
        'Apache RTR 160',
        'Apache RTR 200',
        'Raider 125',
        'Sport 100',
    ],
    'Yamaha': [
        'Crypton FI',
        'FZ-S FI',
        'FZ25',
        'MT-03',
        'NMAX 155',
        'XTZ125',
        'XTZ150',
    ],
}


def crear_catalogo_y_migrar_motos(apps, schema_editor):
    MarcaMoto = apps.get_model('app_movimientos', 'MarcaMoto')
    ModeloMoto = apps.get_model('app_movimientos', 'ModeloMoto')
    Moto = apps.get_model('app_movimientos', 'Moto')

    for nombre_marca, modelos in CATALOGO_INICIAL.items():
        marca, _ = MarcaMoto.objects.get_or_create(nombre=nombre_marca)
        for nombre_modelo in modelos:
            ModeloMoto.objects.get_or_create(marca=marca, nombre=nombre_modelo)

    for moto in Moto.objects.all():
        marca, _ = MarcaMoto.objects.get_or_create(nombre=moto.marca.strip())
        modelo, _ = ModeloMoto.objects.get_or_create(
            marca=marca,
            nombre=moto.modelo.strip(),
        )
        moto.marca_catalogo = marca
        moto.modelo_catalogo = modelo
        moto.save(update_fields=['marca_catalogo', 'modelo_catalogo'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0008_motorista_ubicacion_remove_farmacia'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarcaMoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True, verbose_name='Marca')),
            ],
            options={
                'verbose_name': 'Marca de moto',
                'verbose_name_plural': 'Marcas de moto',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='ModeloMoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Modelo')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modelos', to='app_movimientos.marcamoto', verbose_name='Marca')),
            ],
            options={
                'verbose_name': 'Modelo de moto',
                'verbose_name_plural': 'Modelos de moto',
                'ordering': ['marca__nombre', 'nombre'],
            },
        ),
        migrations.AddConstraint(
            model_name='modelomoto',
            constraint=models.UniqueConstraint(fields=('marca', 'nombre'), name='modelo_moto_unico_por_marca'),
        ),
        migrations.AddField(
            model_name='moto',
            name='marca_catalogo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='app_movimientos.marcamoto'),
        ),
        migrations.AddField(
            model_name='moto',
            name='modelo_catalogo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='app_movimientos.modelomoto'),
        ),
        migrations.RunPython(crear_catalogo_y_migrar_motos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='moto',
            name='marca',
        ),
        migrations.RemoveField(
            model_name='moto',
            name='modelo',
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    'ALTER TABLE app_movimientos_moto '
                    'CHANGE COLUMN marca_catalogo_id marca_id bigint NULL',
                    reverse_sql=(
                        'ALTER TABLE app_movimientos_moto '
                        'CHANGE COLUMN marca_id marca_catalogo_id bigint NULL'
                    ),
                ),
                migrations.RunSQL(
                    'ALTER TABLE app_movimientos_moto '
                    'CHANGE COLUMN modelo_catalogo_id modelo_id bigint NULL',
                    reverse_sql=(
                        'ALTER TABLE app_movimientos_moto '
                        'CHANGE COLUMN modelo_id modelo_catalogo_id bigint NULL'
                    ),
                ),
            ],
            state_operations=[
                migrations.RenameField(
                    model_name='moto',
                    old_name='marca_catalogo',
                    new_name='marca',
                ),
                migrations.RenameField(
                    model_name='moto',
                    old_name='modelo_catalogo',
                    new_name='modelo',
                ),
            ],
        ),
        migrations.AlterField(
            model_name='moto',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='motos', to='app_movimientos.marcamoto', verbose_name='Marca'),
        ),
        migrations.AlterField(
            model_name='moto',
            name='modelo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='motos', to='app_movimientos.modelomoto', verbose_name='Modelo'),
        ),
    ]
