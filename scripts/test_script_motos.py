from app_movimientos.models import MarcaMoto, ModeloMoto, Moto

marcas_modelos = [
    ('Honda', 'CB190R'), ('Yamaha', 'FZ25'), ('Suzuki', 'GN125'),
    ('Bajaj', 'Pulsar NS200'), ('Kawasaki', 'Z400'), ('KTM', 'Duke 200'),
    ('Hero', 'Hunk 160R'), ('TVS', 'Apache RTR 160'), ('Benelli', 'TNT 150'),
    ('Royal Enfield', 'Hunter 350'), ('Zontes', 'U1 155'), ('CFMoto', 'NK 250'),
    ('Voge', '300AC'), ('Loncin', 'LX200'), ('Lifan', 'KPR 200'),
    ('Keeway', 'RKF 125'), ('Haojue', 'DR160'), ('Aprilia', 'Tuono 125'),
    ('Piaggio', 'Liberty 150'), ('SYM', 'NH-T 200'),
]

estados = ['DISPONIBLE', 'DISPONIBLE', 'DISPONIBLE', 'MANTENCION']

for i, (marca_nombre, modelo_nombre) in enumerate(marcas_modelos, start=1):
    marca, _ = MarcaMoto.objects.update_or_create(nombre=marca_nombre)
    modelo, _ = ModeloMoto.objects.update_or_create(
        marca=marca,
        nombre=modelo_nombre,
    )

    moto, _ = Moto.objects.update_or_create(
        patente=f'DP{i:04d}',
        defaults={
            'marca': marca,
            'modelo': modelo,
            'anio': 2020 + (i % 6),
            'estado': estados[(i - 1) % len(estados)],
        },
    )

    moto.full_clean()
    moto.save()

print('Motos creadas/actualizadas:', Moto.objects.count())
