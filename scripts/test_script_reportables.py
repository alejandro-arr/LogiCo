from django.contrib.auth import get_user_model
from django.utils import timezone

from app_movimientos.models import (
    Farmacia,
    Motorista,
    Moto,
    AsignacionMotorista,
    AsignacionTurno,
    Movimiento,
)

farmacias = list(Farmacia.objects.order_by('id')[:20])
motoristas = list(Motorista.objects.order_by('id')[:20])
motos = list(Moto.objects.order_by('id')[:20])

if len(farmacias) < 20 or len(motoristas) < 20 or len(motos) < 20:
    raise Exception('Necesitas al menos 20 farmacias, 20 motoristas y 20 motos.')

admin = get_user_model().objects.filter(username='admin').first()
hoy = timezone.localdate()

tipos = ['DIRECTO', 'RECETA', 'TRASLADO', 'REENVIO']

for i in range(20):
    farmacia = farmacias[i]
    motorista = motoristas[i]
    moto = motos[i]
    tipo = tipos[i % len(tipos)]

    AsignacionMotorista.objects.update_or_create(
        motorista=motorista,
        defaults={
            'farmacia': farmacia,
            'observaciones': f'Asignación para reporte {i + 1:02d}.',
        },
    )

    turno, _ = AsignacionTurno.objects.update_or_create(
        motorista=motorista,
        fecha=hoy,
        defaults={
            'farmacia': farmacia,
            'moto': moto,
            'es_reemplazo': False,
            'observaciones': f'Turno para reporte {i + 1:02d}.',
        },
    )

    farmacia_destino = None
    if tipo == 'TRASLADO':
        farmacia_destino = farmacias[(i + 5) % len(farmacias)]

    movimiento, _ = Movimiento.objects.update_or_create(
        codigo=f'REP-DEMO-{i + 1:03d}',
        defaults={
            'farmacia_origen': farmacia,
            'farmacia_destino': farmacia_destino,
            'motorista': motorista,
            'asignacion_turno': turno,
            'direccion_destino': f'Dirección Reporte {i + 1:02d}, {farmacia.comuna}',
            'observaciones': f'Pedido validado para reporte {i + 1:02d}.',
            'estado': 'ENTREGADO',
            'tipo_movimiento': tipo,
            'validado': True,
            'fecha_validacion': timezone.now(),
            'validado_por': admin,
            'fecha_anulacion': None,
            'anulado_por': None,
            'motivo_anulacion': '',
        },
    )

    movimiento.full_clean()
    movimiento.save()

print('Movimientos reportables creados/actualizados:', Movimiento.objects.filter(
    estado='ENTREGADO',
    validado=True,
).count())
