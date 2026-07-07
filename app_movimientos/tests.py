from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AsignacionMotoristaForm,
    FarmaciaForm,
    MotoForm,
    MotoristaForm,
    MovimientoForm,
)
from .models import (
    AsignacionMotorista,
    AsignacionTurno,
    Farmacia,
    MarcaMoto,
    ModeloMoto,
    Moto,
    Motorista,
    Movimiento,
)


class FarmaciaMotoristaTests(TestCase):
    def setUp(self):
        self.farmacia = Farmacia.objects.create(
            nombre_local='Farmacia Centro',
            direccion='Av. Principal 123',
            telefono='221234567',
            encargado='Ana Pérez',
            region='METROPOLITANA',
        )

    def test_farmacia_form_exige_region(self):
        form = FarmaciaForm(data={
            'nombre_local': 'Farmacia Norte',
            'direccion': 'Calle Norte 456',
            'telefono': '221111111',
            'encargado': 'Luis Soto',
            'region': '',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('region', form.errors)

    def test_farmacia_form_guarda_provincia_y_comuna_validas(self):
        form = FarmaciaForm(data={
            'nombre_local': 'Farmacia Norte',
            'direccion': 'Calle Norte 456',
            'telefono': '221111111',
            'encargado': 'Luis Soto',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Providencia',
        })

        self.assertTrue(form.is_valid(), form.errors)
        farmacia = form.save()
        self.assertEqual(farmacia.provincia, 'Santiago')
        self.assertEqual(farmacia.comuna, 'Providencia')

    def test_farmacia_form_rechaza_comuna_de_otra_provincia(self):
        form = FarmaciaForm(data={
            'nombre_local': 'Farmacia Norte',
            'direccion': 'Calle Norte 456',
            'telefono': '221111111',
            'encargado': 'Luis Soto',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Puente Alto',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('comuna', form.errors)

    def test_formulario_carga_provincias_y_comunas_al_editar(self):
        self.farmacia.provincia = 'Santiago'
        self.farmacia.comuna = 'Providencia'
        self.farmacia.save()

        form = FarmaciaForm(instance=self.farmacia)

        self.assertIn(('Santiago', 'Santiago'), form.fields['provincia'].choices)
        self.assertIn(('Providencia', 'Providencia'), form.fields['comuna'].choices)

    def test_motorista_form_guarda_ubicacion_sin_asignar_farmacia(self):
        form = MotoristaForm(data={
            'rut': '11.111.111-1',
            'nombre_completo': 'María López',
            'telefono': '912345678',
            'estado': 'ACTIVO',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Providencia',
        })

        self.assertTrue(form.is_valid(), form.errors)
        motorista = form.save()
        self.assertEqual(motorista.region, 'METROPOLITANA')
        self.assertEqual(motorista.provincia, 'Santiago')
        self.assertEqual(motorista.comuna, 'Providencia')
        self.assertNotIn('farmacia', form.fields)

    def test_motorista_form_rechaza_rut_invalido(self):
        form = MotoristaForm(data={
            'rut': '12.345.678-9',
            'nombre_completo': 'Rut Inválido',
            'telefono': '912345678',
            'estado': 'ACTIVO',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Providencia',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('rut', form.errors)

    def test_motorista_form_normaliza_rut_valido_sin_formato(self):
        form = MotoristaForm(data={
            'rut': '12345678-5',
            'nombre_completo': 'Rut Válido',
            'telefono': '912345678',
            'estado': 'ACTIVO',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Providencia',
        })

        self.assertTrue(form.is_valid(), form.errors)
        motorista = form.save()
        self.assertEqual(motorista.rut, '12.345.678-5')

    def test_motorista_form_acepta_digito_k_minuscula(self):
        form = MotoristaForm(data={
            'rut': '1000005-k',
            'nombre_completo': 'Rut con K',
            'telefono': '912345678',
            'estado': 'ACTIVO',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Providencia',
        })

        self.assertTrue(form.is_valid(), form.errors)
        motorista = form.save()
        self.assertEqual(motorista.rut, '1.000.005-K')

    def test_motorista_form_rechaza_ubicacion_invalida(self):
        form = MotoristaForm(data={
            'rut': '12.345.678-5',
            'nombre_completo': 'Pedro González',
            'telefono': '987654321',
            'estado': 'ACTIVO',
            'region': 'METROPOLITANA',
            'provincia': 'Santiago',
            'comuna': 'Puente Alto',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('comuna', form.errors)


class ReportesTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='reportes',
            password='ClaveSegura123',
        )
        self.farmacia = Farmacia.objects.create(
            nombre_local='Farmacia Reportes',
            direccion='Av. Reportes 100',
            telefono='221234567',
            encargado='Ana Pérez',
            region='METROPOLITANA',
        )
        self.motorista = Motorista.objects.create(
            rut='10.000.000-8',
            nombre_completo='Motorista Reportes',
            telefono='987654321',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Santiago',
        )
        AsignacionMotorista.objects.create(
            motorista=self.motorista,
            farmacia=self.farmacia,
        )
        self.moto = Moto.objects.create(
            patente='ABCD12',
            marca=MarcaMoto.objects.get(nombre='Honda'),
            modelo=ModeloMoto.objects.get(marca__nombre='Honda', nombre='CB190R'),
            anio=2025,
        )
        self.asignacion = AsignacionTurno.objects.create(
            farmacia=self.farmacia,
            motorista=self.motorista,
            moto=self.moto,
            fecha=timezone.localdate(),
        )

    def test_no_permite_validar_pedido_no_entregado(self):
        form = MovimientoForm(data={
            'codigo': 'MOV-VALIDACION',
            'farmacia_origen': self.farmacia.pk,
            'motorista': self.motorista.pk,
            'direccion_destino': 'Calle Uno 123',
            'observaciones': 'Pedido pendiente de entrega.',
            'estado': 'PENDIENTE',
            'tipo_movimiento': 'DIRECTO',
            'validado': True,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('validado', form.errors)

    def test_reporte_muestra_solo_entregados_validados_del_periodo(self):
        incluido = Movimiento.objects.create(
            farmacia_origen=self.farmacia,
            motorista=self.motorista,
            asignacion_turno=self.asignacion,
            direccion_destino='Calle Incluida 123',
            estado='ENTREGADO',
            validado=True,
            fecha_validacion=timezone.now(),
            validado_por=self.usuario,
        )
        Movimiento.objects.create(
            farmacia_origen=self.farmacia,
            motorista=self.motorista,
            asignacion_turno=self.asignacion,
            direccion_destino='Calle No Validada 456',
            estado='ENTREGADO',
            validado=False,
        )
        antiguo = Movimiento.objects.create(
            farmacia_origen=self.farmacia,
            motorista=self.motorista,
            asignacion_turno=self.asignacion,
            direccion_destino='Calle Antigua 789',
            estado='ENTREGADO',
            validado=True,
            fecha_validacion=timezone.now(),
        )
        Movimiento.objects.filter(pk=antiguo.pk).update(
            fecha_hora=timezone.now() - timedelta(days=40),
        )

        self.client.force_login(self.usuario)
        hoy = timezone.localdate().isoformat()
        response = self.client.get(reverse('reportes'), {
            'periodo': 'diario',
            'fecha': hoy,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, incluido.direccion_destino)
        self.assertNotContains(response, 'Calle No Validada 456')
        self.assertNotContains(response, antiguo.direccion_destino)
        self.assertEqual(response.context['total_pedidos'], 1)


class MotoFiltrosTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='motos',
            password='ClaveSegura123',
        )
        self.honda = Moto.objects.create(
            patente='ABCD12',
            marca=MarcaMoto.objects.get(nombre='Honda'),
            modelo=ModeloMoto.objects.get(marca__nombre='Honda', nombre='CB190R'),
            anio=2025,
            estado='DISPONIBLE',
        )
        self.yamaha = Moto.objects.create(
            patente='WXYZ98',
            marca=MarcaMoto.objects.get(nombre='Yamaha'),
            modelo=ModeloMoto.objects.get(marca__nombre='Yamaha', nombre='FZ25'),
            anio=2024,
            estado='MANTENCION',
        )
        self.client.force_login(self.usuario)

    def test_busca_moto_por_patente_marca_o_modelo(self):
        for busqueda in ('ABCD12', 'Honda', 'CB190R'):
            with self.subTest(busqueda=busqueda):
                response = self.client.get(reverse('moto_list'), {'q': busqueda})
                self.assertContains(response, self.honda.patente)
                self.assertNotContains(response, self.yamaha.patente)

    def test_filtra_motos_por_estado(self):
        response = self.client.get(reverse('moto_list'), {
            'estado': 'MANTENCION',
        })

        self.assertContains(response, self.yamaha.patente)
        self.assertNotContains(response, self.honda.patente)

    def test_combina_busqueda_y_estado(self):
        response = self.client.get(reverse('moto_list'), {
            'q': 'Yamaha',
            'estado': 'DISPONIBLE',
        })

        self.assertNotContains(response, self.honda.patente)
        self.assertNotContains(response, self.yamaha.patente)
        self.assertContains(response, '0 motos encontradas.')


class MotoristaFiltrosTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='filtros_motoristas',
            password='ClaveSegura123',
        )
        self.metropolitano = Motorista.objects.create(
            rut='10.111.111-1',
            nombre_completo='Carlos Santiago',
            telefono='911111111',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Santiago',
        )
        self.valparaiso = Motorista.objects.create(
            rut='20.222.222-2',
            nombre_completo='Andrea Valparaíso',
            telefono='922222222',
            region='VALPARAISO',
            provincia='Valparaíso',
            comuna='Valparaíso',
        )
        self.client.force_login(self.usuario)

    def test_busca_motorista_por_nombre(self):
        response = self.client.get(reverse('motorista_list'), {'q': 'Carlos'})

        self.assertContains(response, self.metropolitano.nombre_completo)
        self.assertNotContains(response, self.valparaiso.nombre_completo)

    def test_filtra_motoristas_por_region(self):
        response = self.client.get(reverse('motorista_list'), {
            'region': 'VALPARAISO',
        })

        self.assertContains(response, self.valparaiso.nombre_completo)
        self.assertNotContains(response, self.metropolitano.nombre_completo)

    def test_combina_nombre_y_region(self):
        response = self.client.get(reverse('motorista_list'), {
            'q': 'Carlos',
            'region': 'VALPARAISO',
        })

        self.assertNotContains(response, self.metropolitano.nombre_completo)
        self.assertNotContains(response, self.valparaiso.nombre_completo)
        self.assertContains(response, '0 motoristas encontrados.')


class MotoCatalogoTests(TestCase):
    def setUp(self):
        self.honda = MarcaMoto.objects.get(nombre='Honda')
        self.yamaha = MarcaMoto.objects.get(nombre='Yamaha')
        self.cb190r = ModeloMoto.objects.get(marca=self.honda, nombre='CB190R')
        self.fz25 = ModeloMoto.objects.get(marca=self.yamaha, nombre='FZ25')

    def test_filtra_modelos_segun_marca(self):
        form = MotoForm(data={
            'patente': 'TEST12',
            'marca': self.honda.pk,
            'modelo': self.cb190r.pk,
            'anio': 2025,
            'estado': 'DISPONIBLE',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn(self.cb190r, form.fields['modelo'].queryset)
        self.assertNotIn(self.fz25, form.fields['modelo'].queryset)

    def test_rechaza_modelo_de_otra_marca(self):
        form = MotoForm(data={
            'patente': 'TEST34',
            'marca': self.honda.pk,
            'modelo': self.fz25.pk,
            'anio': 2025,
            'estado': 'DISPONIBLE',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('modelo', form.errors)


class AsignacionMotoristaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='asignaciones',
            password='ClaveSegura123',
        )
        self.motorista = Motorista.objects.create(
            rut='18.765.432-1',
            nombre_completo='Motorista Asignable',
            telefono='987654321',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Providencia',
        )
        self.farmacia_centro = Farmacia.objects.create(
            nombre_local='Farmacia Centro',
            direccion='Av. Centro 100',
            telefono='221111111',
            encargado='Ana Pérez',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Santiago',
        )
        self.farmacia_norte = Farmacia.objects.create(
            nombre_local='Farmacia Norte',
            direccion='Av. Norte 200',
            telefono='222222222',
            encargado='Luis Soto',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Quilicura',
        )
        self.client.force_login(self.usuario)

    def test_crea_asignacion_desde_interfaz(self):
        response = self.client.post(reverse('asignacion_create'), {
            'motorista': self.motorista.pk,
            'farmacia': self.farmacia_centro.pk,
            'observaciones': 'Turno habitual.',
        })

        self.assertRedirects(response, reverse('asignacion_list'))
        asignacion = AsignacionMotorista.objects.get(motorista=self.motorista)
        self.assertEqual(asignacion.farmacia, self.farmacia_centro)

    def test_no_ofrece_motoristas_que_ya_estan_asignados(self):
        AsignacionMotorista.objects.create(
            motorista=self.motorista,
            farmacia=self.farmacia_centro,
        )

        form = AsignacionMotoristaForm()

        self.assertNotIn(self.motorista, form.fields['motorista'].queryset)

    def test_permite_reasignar_motorista(self):
        asignacion = AsignacionMotorista.objects.create(
            motorista=self.motorista,
            farmacia=self.farmacia_centro,
        )

        response = self.client.post(
            reverse('asignacion_update', args=[asignacion.pk]),
            {
                'motorista': self.motorista.pk,
                'farmacia': self.farmacia_norte.pk,
                'observaciones': 'Cambio de cobertura.',
            },
        )

        self.assertRedirects(response, reverse('asignacion_list'))
        asignacion.refresh_from_db()
        self.assertEqual(asignacion.farmacia, self.farmacia_norte)

    def test_lista_muestra_motorista_y_farmacia(self):
        AsignacionMotorista.objects.create(
            motorista=self.motorista,
            farmacia=self.farmacia_centro,
        )

        response = self.client.get(reverse('asignacion_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.motorista.nombre_completo)
        self.assertContains(response, self.farmacia_centro.nombre_local)


class OperacionesMovimientoTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username='operaciones',
            password='ClaveSegura123',
        )
        farmacia = Farmacia.objects.create(
            nombre_local='Farmacia Operaciones',
            direccion='Av. Operaciones 100',
            telefono='221234567',
            encargado='Ana Pérez',
            region='METROPOLITANA',
        )
        self.farmacia_destino = Farmacia.objects.create(
            nombre_local='Farmacia Destino',
            direccion='Av. Destino 200',
            telefono='224444444',
            encargado='Paula Reyes',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Providencia',
        )
        motorista = Motorista.objects.create(
            rut='15.000.000-1',
            nombre_completo='Motorista Operaciones',
            telefono='987654321',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Santiago',
        )
        moto = Moto.objects.create(
            patente='OPER12',
            marca=MarcaMoto.objects.get(nombre='Honda'),
            modelo=ModeloMoto.objects.get(marca__nombre='Honda', nombre='CB190R'),
            anio=2025,
        )
        self.asignacion = AsignacionTurno.objects.create(
            farmacia=farmacia,
            motorista=motorista,
            moto=moto,
            fecha=timezone.localdate(),
        )
        AsignacionMotorista.objects.create(
            motorista=motorista,
            farmacia=farmacia,
        )
        self.client.force_login(self.usuario)

    def test_cada_ruta_crea_el_tipo_de_movimiento_correcto(self):
        rutas = {
            'movimiento_directo_create': 'DIRECTO',
            'movimiento_receta_create': 'RECETA',
            'movimiento_traslado_create': 'TRASLADO',
            'movimiento_reenvio_create': 'REENVIO',
        }

        for indice, (ruta, tipo) in enumerate(rutas.items(), start=1):
            with self.subTest(tipo=tipo):
                datos = {
                    'codigo': f'MOV-OPER-{indice}',
                    'farmacia_origen': self.asignacion.farmacia_id,
                    'motorista': self.asignacion.motorista_id,
                    'direccion_destino': f'Calle Operación {indice}',
                    'observaciones': f'Observación operación {indice}',
                    'estado': 'PENDIENTE',
                }
                if tipo == 'TRASLADO':
                    datos['farmacia_destino'] = self.farmacia_destino.pk
                response = self.client.post(reverse(ruta), datos)

                self.assertRedirects(response, reverse('movimientos_list'))
                self.assertTrue(Movimiento.objects.filter(
                    direccion_destino=f'Calle Operación {indice}',
                    tipo_movimiento=tipo,
                ).exists())
                movimiento = Movimiento.objects.get(
                    direccion_destino=f'Calle Operación {indice}',
                )
                if tipo == 'TRASLADO':
                    self.assertEqual(
                        movimiento.farmacia_destino,
                        self.farmacia_destino,
                    )
                else:
                    self.assertIsNone(movimiento.farmacia_destino)

    def test_formulario_normal_no_permite_elegir_estado_anulado(self):
        response = self.client.get(reverse('movimiento_directo_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Origen del movimiento')
        self.assertContains(response, 'Motorista')
        self.assertNotContains(response, 'Turno Asignado')
        self.assertNotContains(response, '<option value="ANULADO">', html=True)

    def test_farmacia_destino_solo_aparece_en_traslados(self):
        traslado = self.client.get(reverse('movimiento_traslado_create'))
        directo = self.client.get(reverse('movimiento_directo_create'))

        self.assertContains(traslado, 'Farmacia de destino')
        self.assertNotContains(directo, 'Farmacia de destino')

    def test_traslado_rechaza_mismo_origen_y_destino(self):
        response = self.client.post(reverse('movimiento_traslado_create'), {
            'codigo': 'MOV-TRASLADO-INVALIDO',
            'farmacia_origen': self.asignacion.farmacia_id,
            'farmacia_destino': self.asignacion.farmacia_id,
            'motorista': self.asignacion.motorista_id,
            'direccion_destino': 'Farmacia de origen',
            'estado': 'PENDIENTE',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'La farmacia de destino debe ser distinta del origen.',
        )
        self.assertFalse(
            Movimiento.objects.filter(codigo='MOV-TRASLADO-INVALIDO').exists()
        )

    def test_movimiento_nuevo_guarda_farmacia_sin_exigir_turno(self):
        response = self.client.post(reverse('movimiento_directo_create'), {
            'codigo': 'MOV-ORIGEN-1',
            'farmacia_origen': self.asignacion.farmacia_id,
            'motorista': self.asignacion.motorista_id,
            'direccion_destino': 'Calle Origen 123',
            'observaciones': 'Entregar en recepción.',
            'estado': 'PENDIENTE',
        })

        self.assertRedirects(response, reverse('movimientos_list'))
        movimiento = Movimiento.objects.get(direccion_destino='Calle Origen 123')
        self.assertEqual(movimiento.farmacia_origen, self.asignacion.farmacia)
        self.assertEqual(movimiento.motorista, self.asignacion.motorista)
        self.assertEqual(movimiento.codigo, 'MOV-ORIGEN-1')
        self.assertEqual(movimiento.observaciones, 'Entregar en recepción.')
        self.assertIsNone(movimiento.asignacion_turno)

    def test_rechaza_motorista_asignado_a_otra_farmacia(self):
        otra_farmacia = Farmacia.objects.create(
            nombre_local='Farmacia Alternativa',
            direccion='Av. Alternativa 200',
            telefono='223333333',
            encargado='Elena Díaz',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Providencia',
        )
        otro_motorista = Motorista.objects.create(
            rut='16.111.111-2',
            nombre_completo='Motorista Alternativo',
            telefono='933333333',
            region='METROPOLITANA',
            provincia='Santiago',
            comuna='Providencia',
        )
        AsignacionMotorista.objects.create(
            motorista=otro_motorista,
            farmacia=otra_farmacia,
        )

        response = self.client.post(reverse('movimiento_directo_create'), {
            'codigo': 'MOV-INVALIDO-1',
            'farmacia_origen': self.asignacion.farmacia_id,
            'motorista': otro_motorista.pk,
            'direccion_destino': 'Calle Inválida 999',
            'estado': 'PENDIENTE',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'El motorista seleccionado no está asignado a la farmacia de origen.',
        )
        self.assertFalse(
            Movimiento.objects.filter(direccion_destino='Calle Inválida 999').exists()
        )

    def test_busca_movimiento_por_codigo(self):
        Movimiento.objects.create(
            codigo='MOV-BUSCADO-25',
            farmacia_origen=self.asignacion.farmacia,
            motorista=self.asignacion.motorista,
            direccion_destino='Calle Buscada 250',
            observaciones='Referencia de búsqueda.',
        )
        Movimiento.objects.create(
            codigo='MOV-OTRO-26',
            farmacia_origen=self.asignacion.farmacia,
            motorista=self.asignacion.motorista,
            direccion_destino='Calle Diferente 260',
        )

        response = self.client.get(reverse('movimientos_list'), {
            'q': 'MOV-BUSCADO-25',
        })

        self.assertContains(response, 'MOV-BUSCADO-25')
        self.assertNotContains(response, 'MOV-OTRO-26')

    def test_anular_movimiento_conserva_registro_y_auditoria(self):
        movimiento = Movimiento.objects.create(
            farmacia_origen=self.asignacion.farmacia,
            motorista=self.asignacion.motorista,
            asignacion_turno=self.asignacion,
            direccion_destino='Calle Anulación 123',
            estado='ENTREGADO',
            tipo_movimiento='RECETA',
            validado=True,
            fecha_validacion=timezone.now(),
            validado_por=self.usuario,
        )

        response = self.client.post(reverse('movimiento_anular', args=[movimiento.pk]), {
            'motivo_anulacion': 'Dirección ingresada incorrectamente.',
        })

        self.assertRedirects(response, reverse('movimientos_list'))
        movimiento.refresh_from_db()
        self.assertEqual(movimiento.estado, 'ANULADO')
        self.assertEqual(movimiento.anulado_por, self.usuario)
        self.assertIsNotNone(movimiento.fecha_anulacion)
        self.assertEqual(movimiento.motivo_anulacion, 'Dirección ingresada incorrectamente.')
        self.assertFalse(movimiento.validado)
        self.assertIsNone(movimiento.fecha_validacion)
        self.assertTrue(Movimiento.objects.filter(pk=movimiento.pk).exists())
