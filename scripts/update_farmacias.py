from app_movimientos.models import Farmacia

farmacias = Farmacia.objects.filter(nombre_local__icontains='Farmacia Discopro')
count = 0
for f in farmacias:
    f.nombre_local = f.nombre_local.replace('Farmacia Discopro', 'Farmacia Cruz Verde')
    f.save()
    count += 1

print(f'Farmacias actualizadas: {count}')
