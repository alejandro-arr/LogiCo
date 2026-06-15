from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_movimientos', '0010_asignacion_motorista'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuariosistema',
            name='rol',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Admin'),
                    ('GERENTE', 'Gerente'),
                    ('SUPERVISOR', 'Supervisor'),
                    ('MOTORISTA', 'Motorista'),
                    ('GENERICO', 'Usuario generico'),
                ],
                default='GENERICO',
                max_length=20,
                verbose_name='Rol',
            ),
        ),
    ]
