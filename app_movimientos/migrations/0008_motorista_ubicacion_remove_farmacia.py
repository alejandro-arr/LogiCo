from django.db import migrations, models


def copiar_ubicacion_desde_farmacia(apps, schema_editor):
    Motorista = apps.get_model('app_movimientos', 'Motorista')
    for motorista in Motorista.objects.select_related('farmacia'):
        if motorista.farmacia:
            motorista.region = motorista.farmacia.region
            motorista.provincia = motorista.farmacia.provincia
            motorista.comuna = motorista.farmacia.comuna
            motorista.save(update_fields=['region', 'provincia', 'comuna'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0007_farmacia_provincia_comuna'),
    ]

    operations = [
        migrations.AddField(
            model_name='motorista',
            name='region',
            field=models.CharField(
                choices=[
                    ('ARICA_PARINACOTA', 'Región de Arica y Parinacota'),
                    ('TARAPACA', 'Región de Tarapacá'),
                    ('ANTOFAGASTA', 'Región de Antofagasta'),
                    ('ATACAMA', 'Región de Atacama'),
                    ('COQUIMBO', 'Región de Coquimbo'),
                    ('VALPARAISO', 'Región de Valparaíso'),
                    ('METROPOLITANA', 'Región Metropolitana de Santiago'),
                    ('OHIGGINS', "Región del Libertador General Bernardo O'Higgins"),
                    ('MAULE', 'Región del Maule'),
                    ('NUBLE', 'Región de Ñuble'),
                    ('BIOBIO', 'Región del Biobío'),
                    ('ARAUCANIA', 'Región de La Araucanía'),
                    ('LOS_RIOS', 'Región de Los Ríos'),
                    ('LOS_LAGOS', 'Región de Los Lagos'),
                    ('AYSEN', 'Región de Aysén del General Carlos Ibáñez del Campo'),
                    ('MAGALLANES', 'Región de Magallanes y de la Antártica Chilena'),
                ],
                default='',
                max_length=20,
                verbose_name='Región',
            ),
        ),
        migrations.AddField(
            model_name='motorista',
            name='provincia',
            field=models.CharField(default='', max_length=100, verbose_name='Provincia'),
        ),
        migrations.AddField(
            model_name='motorista',
            name='comuna',
            field=models.CharField(default='', max_length=100, verbose_name='Comuna'),
        ),
        migrations.RunPython(copiar_ubicacion_desde_farmacia, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='motorista',
            name='farmacia',
        ),
    ]
