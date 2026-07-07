import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_logico.settings')
django.setup()

from app_movimientos.models import Motorista, calcular_digito_verificador_rut, formatear_rut

nombres = [
    'Camila Morales', 'Joaquin Herrera', 'Sofia Castillo', 'Tomas Vargas',
    'Fernanda Silva', 'Ignacio Navarro', 'Catalina Fuentes', 'Benjamin Soto',
    'Martin Vega', 'Isidora Contreras', 'Sebastian Munoz', 'Josefa Araya',
    'Vicente Medina', 'Florencia Carrasco', 'Agustin Paredes',
    'Trinidad Aguilera', 'Amanda Espinoza', 'Maximiliano Campos',
    'Martina Valdes', 'Cristobal Molina',
]

ubicaciones = [
    ('METROPOLITANA', 'Santiago', 'Santiago'),
    ('METROPOLITANA', 'Santiago', 'Providencia'),
    ('METROPOLITANA', 'Santiago', 'Las Condes'),
    ('METROPOLITANA', 'Santiago', 'Ñuñoa'),
    ('METROPOLITANA', 'Santiago', 'Maipú'),
    ('VALPARAISO', 'Valparaíso', 'Valparaíso'),
    ('VALPARAISO', 'Valparaíso', 'Viña del Mar'),
    ('BIOBIO', 'Concepción', 'Concepción'),
    ('BIOBIO', 'Concepción', 'Talcahuano'),
    ('ARAUCANIA', 'Cautín', 'Temuco'),
    ('LOS_LAGOS', 'Llanquihue', 'Puerto Montt'),
    ('COQUIMBO', 'Elqui', 'La Serena'),
    ('ANTOFAGASTA', 'Antofagasta', 'Antofagasta'),
    ('MAULE', 'Talca', 'Talca'),
    ('NUBLE', 'Diguillín', 'Chillán'),
    ('OHIGGINS', 'Cachapoal', 'Rancagua'),
    ('LOS_RIOS', 'Valdivia', 'Valdivia'),
    ('ATACAMA', 'Copiapó', 'Copiapó'),
    ('TARAPACA', 'Iquique', 'Iquique'),
    ('ARICA_PARINACOTA', 'Arica', 'Arica'),
]

for i, nombre in enumerate(nombres, start=1):
    cuerpo_rut = str(20000000 + i)
    rut = formatear_rut(f'{cuerpo_rut}-{calcular_digito_verificador_rut(cuerpo_rut)}')
    region, provincia, comuna = ubicaciones[i - 1]

    motorista, creado = Motorista.objects.update_or_create(
        rut=rut,
        defaults={
            'nombre_completo': nombre,
            'telefono': f'9{30000000 + i:08d}',
            'estado': 'ACTIVO' if i % 5 else 'INACTIVO',
            'region': region,
            'provincia': provincia,
            'comuna': comuna,
        },
    )

    motorista.full_clean()
    motorista.save()

print('Motoristas creados/actualizados:', Motorista.objects.count())
