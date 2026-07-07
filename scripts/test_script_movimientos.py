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
    raise Exception('Necesitas al menos 20 farmacias, 20 motoristas y 20 motos antes de crear movimientos.')

admin = get_user_model().objects.filter(username='admin').first()
hoy = timezone.localdate()

tipos = ['DIRECTO', 'RECETA', 'TRASLADO', 'REENVIO']
estados = ['ENTREGADO', 'PENDIENTE', 'EN_RUTA', 'ENTREGADO', 'FALLIDO', 'ANULADO']

for i in range(20):
    farmacia = farmacias[i]
    motorista = motoristas[i]
    moto = motos[i]

    AsignacionMotorista.objects.update_or_create(
        motorista=motorista,
        defaults={
            'farmacia': farmacia,
            'observaciones': f'Asignación demo para movimiento {i + 1:02d}.',
        },
    )

    turno, _ = AsignacionTurno.objects.update_or_create(
        motorista=motorista,
        fecha=hoy,
        defaults={
            'farmacia': farmacia,
            'moto': moto,
            'es_reemplazo': False,
            'observaciones': f'Turno demo {i + 1:02d}.',
        },
    )

    tipo = tipos[i % len(tipos)]
    estado = estados[i % len(estados)]
    validado = estado == 'ENTREGADO'

    farmacia_destino = None
    if tipo == 'TRASLADO':
        farmacia_destino = farmacias[(i + 5) % len(farmacias)]
        if farmacia_destino == farmacia:
            farmacia_destino = farmacias[(i + 6) % len(farmacias)]

    movimiento, _ = Movimiento.objects.update_or_create(
        codigo=f'MOV-DEMO-{i + 1:03d}',
        defaults={
            'farmacia_origen': farmacia,
            'farmacia_destino': farmacia_destino,
            'motorista': motorista,
            'asignacion_turno': turno,
            'direccion_destino': f'Calle Demo {500 + i + 1}, {farmacia.comuna}',
            'observaciones': f'Movimiento de demostración {i + 1:02d}.',
            'estado': estado,
            'tipo_movimiento': tipo,
            'validado': validado,
            'fecha_validacion': timezone.now() if validado else None,
            'validado_por': admin if validado else None,
            'fecha_anulacion': timezone.now() if estado == 'ANULADO' else None,
            'anulado_por': admin if estado == 'ANULADO' else None,
            'motivo_anulacion': 'Registro de demostración anulado.' if estado == 'ANULADO' else '',
        },
    )

    movimiento.full_clean()
    movimiento.save()

print('Movimientos creados/actualizados:', Movimiento.objects.count())
