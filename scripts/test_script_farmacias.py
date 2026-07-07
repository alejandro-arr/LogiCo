from app_movimientos.models import Farmacia

datos_farmacias = [
    ('Farmacia Discopro 01', 'Av. Principal 101, Santiago', '221000001', 'Camila Morales', 'METROPOLITANA', 'Santiago', 'Santiago'),
    ('Farmacia Discopro 02', 'Av. Principal 102, Providencia', '221000002', 'Joaquin Herrera', 'METROPOLITANA', 'Santiago', 'Providencia'),
    ('Farmacia Discopro 03', 'Av. Principal 103, Las Condes', '221000003', 'Sofia Castillo', 'METROPOLITANA', 'Santiago', 'Las Condes'),
    ('Farmacia Discopro 04', 'Av. Principal 104, Ñuñoa', '221000004', 'Tomas Vargas', 'METROPOLITANA', 'Santiago', 'Ñuñoa'),
    ('Farmacia Discopro 05', 'Av. Principal 105, Maipú', '221000005', 'Fernanda Silva', 'METROPOLITANA', 'Santiago', 'Maipú'),
    ('Farmacia Discopro 06', 'Av. Valparaíso 106, Valparaíso', '221000006', 'Ignacio Navarro', 'VALPARAISO', 'Valparaíso', 'Valparaíso'),
    ('Farmacia Discopro 07', 'Av. Libertad 107, Viña del Mar', '221000007', 'Catalina Fuentes', 'VALPARAISO', 'Valparaíso', 'Viña del Mar'),
    ('Farmacia Discopro 08', 'Av. Concepción 108, Concepción', '221000008', 'Benjamin Soto', 'BIOBIO', 'Concepción', 'Concepción'),
    ('Farmacia Discopro 09', 'Av. Colón 109, Talcahuano', '221000009', 'Martin Vega', 'BIOBIO', 'Concepción', 'Talcahuano'),
    ('Farmacia Discopro 10', 'Av. Alemania 110, Temuco', '221000010', 'Isidora Contreras', 'ARAUCANIA', 'Cautín', 'Temuco'),
    ('Farmacia Discopro 11', 'Av. Costanera 111, Puerto Montt', '221000011', 'Sebastian Munoz', 'LOS_LAGOS', 'Llanquihue', 'Puerto Montt'),
    ('Farmacia Discopro 12', 'Av. Francisco de Aguirre 112, La Serena', '221000012', 'Josefa Araya', 'COQUIMBO', 'Elqui', 'La Serena'),
    ('Farmacia Discopro 13', 'Av. Angamos 113, Antofagasta', '221000013', 'Vicente Medina', 'ANTOFAGASTA', 'Antofagasta', 'Antofagasta'),
    ('Farmacia Discopro 14', 'Av. Alameda 114, Talca', '221000014', 'Florencia Carrasco', 'MAULE', 'Talca', 'Talca'),
    ('Farmacia Discopro 15', 'Av. Libertad 115, Chillán', '221000015', 'Agustin Paredes', 'NUBLE', 'Diguillín', 'Chillán'),
    ('Farmacia Discopro 16', 'Av. O Higgins 116, Rancagua', '221000016', 'Trinidad Aguilera', 'OHIGGINS', 'Cachapoal', 'Rancagua'),
    ('Farmacia Discopro 17', 'Av. Picarte 117, Valdivia', '221000017', 'Amanda Espinoza', 'LOS_RIOS', 'Valdivia', 'Valdivia'),
    ('Farmacia Discopro 18', 'Av. Copayapu 118, Copiapó', '221000018', 'Maximiliano Campos', 'ATACAMA', 'Copiapó', 'Copiapó'),
    ('Farmacia Discopro 19', 'Av. Baquedano 119, Iquique', '221000019', 'Martina Valdes', 'TARAPACA', 'Iquique', 'Iquique'),
    ('Farmacia Discopro 20', 'Av. Santa María 120, Arica', '221000020', 'Cristobal Molina', 'ARICA_PARINACOTA', 'Arica', 'Arica'),
]

for nombre, direccion, telefono, encargado, region, provincia, comuna in datos_farmacias:
    Farmacia.objects.update_or_create(
        nombre_local=nombre,
        defaults={
            'direccion': direccion,
            'telefono': telefono,
            'encargado': encargado,
            'region': region,
            'provincia': provincia,
            'comuna': comuna,
        },
    )

print('Farmacias creadas/actualizadas:', Farmacia.objects.count())
