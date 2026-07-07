"""
Módulo de Vistas y Controladores (Django Views & Generic CBVs).

Implementa la lógica de presentación y flujo de control del sistema.
Está dividido en tres capas arquitectónicas:
1. Vistas de Dashboard y Métricas Operativas (KPIs en tiempo real).
2. Clases Base Genéricas (CustomBaseListView, CreateView, etc.) para aplicar DRY en los mantenedores CRUD.
3. Controladores especializados para cada entidad (Despachos, Farmacias, Motoristas, Motos y Turnos).

Buenas prácticas aplicadas:
- Optimización de consultas ORM mediante select_related para evitar el problema N+1 queries.
- Protección de acceso y seguridad vía decoradores @login_required y LoginRequiredMixin.
- Reutilización extrema de código en plantillas (mantenedores genéricos con metadatos de modelos).
"""

import calendar
from datetime import date, datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import (
    AsignacionMotorista,
    AsignacionTurno,
    Farmacia,
    MarcaMoto,
    ModeloMoto,
    Moto,
    Motorista,
    Movimiento,
    UsuarioSistema,
)
from .forms import (
    AnularMovimientoForm,
    AsignacionMotoristaForm,
    AsignacionTurnoForm,
    FarmaciaForm,
    MotoForm,
    MotoristaForm,
    MovimientoForm,
    MovimientoTipoForm,
    UsuarioSistemaForm,
)
from .territorios import TERRITORIOS

# ==================== VISTAS DE DASHBOARD ====================
@login_required
def dashboard_view(request):
    """
    Vista principal del Panel de Control (Dashboard).

    Calcula y muestra métricas clave (KPIs) en tiempo real:
    - Total de despachos registrados y porcentaje de eficiencia (entregados vs total).
    - Estado operativo del personal (motoristas activos) y flota (motos disponibles/en mantención).
    - Últimos 5 movimientos registrados para monitoreo inmediato.
    """
    total_despachos = Movimiento.objects.count()
    motoristas_activos = Motorista.objects.filter(estado='ACTIVO').count()
    motos_disponibles = Moto.objects.filter(estado='DISPONIBLE').count()
    motos_mantencion = Moto.objects.filter(estado='MANTENCION').count()
    
    entregados = Movimiento.objects.filter(estado='ENTREGADO').count()
    eficiencia = int((entregados / total_despachos) * 100) if total_despachos > 0 else 0
        
    ultimos_movimientos = Movimiento.objects.select_related(
        'farmacia_origen',
        'motorista',
    ).all()[:5]

    context = {
        'total_despachos': total_despachos, 'motoristas_activos': motoristas_activos,
        'motos_disponibles': motos_disponibles, 'motos_mantencion': motos_mantencion,
        'eficiencia': eficiencia, 'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'app_movimientos/dashboard.html', context)

@login_required
def movimientos_list_view(request):
    """
    Vista del historial general y buscador de movimientos de despacho.

    Permite filtrar los despachos por código, dirección, observaciones, farmacias de origen/destino
    o nombre del motorista utilizando objetos Q para búsquedas OR eficientes en base de datos.
    """
    busqueda = request.GET.get('q', '').strip()
    movimientos = Movimiento.objects.select_related(
        'farmacia_origen',
        'farmacia_destino',
        'motorista',
        'asignacion_turno__moto',
        'validado_por',
    ).all()
    if busqueda:
        movimientos = movimientos.filter(
            Q(codigo__icontains=busqueda)
            | Q(direccion_destino__icontains=busqueda)
            | Q(observaciones__icontains=busqueda)
            | Q(farmacia_origen__nombre_local__icontains=busqueda)
            | Q(farmacia_destino__nombre_local__icontains=busqueda)
            | Q(motorista__nombre_completo__icontains=busqueda)
        )
    return render(request, 'app_movimientos/movimientos_list.html', {
        'movimientos': movimientos,
        'busqueda': busqueda,
    })


@login_required
def reportes_view(request):
    """
    Vista de generación de Reportes Operativos (diarios, mensuales y anuales).

    Filtra los pedidos que han sido ENTREGADOS y VALIDADOS dentro del rango de fechas estipulado.
    Calcula agregados estadísticos como el número total de pedidos, farmacias activas y motoristas.
    """
    periodo = request.GET.get('periodo', 'diario')
    if periodo not in {'diario', 'mensual', 'anual'}:
        periodo = 'diario'

    hoy = timezone.localdate()
    fecha_texto = request.GET.get('fecha', hoy.isoformat())
    try:
        fecha_referencia = datetime.strptime(fecha_texto, '%Y-%m-%d').date()
    except ValueError:
        fecha_referencia = hoy

    if periodo == 'mensual':
        ultimo_dia = calendar.monthrange(fecha_referencia.year, fecha_referencia.month)[1]
        fecha_inicio = date(fecha_referencia.year, fecha_referencia.month, 1)
        fecha_fin = date(fecha_referencia.year, fecha_referencia.month, ultimo_dia)
        periodo_titulo = fecha_referencia.strftime('%m/%Y')
    elif periodo == 'anual':
        fecha_inicio = date(fecha_referencia.year, 1, 1)
        fecha_fin = date(fecha_referencia.year, 12, 31)
        periodo_titulo = str(fecha_referencia.year)
    else:
        fecha_inicio = fecha_fin = fecha_referencia
        periodo_titulo = fecha_referencia.strftime('%d/%m/%Y')

    pedidos = Movimiento.objects.filter(
        estado='ENTREGADO',
        validado=True,
        fecha_hora__date__range=(fecha_inicio, fecha_fin),
    ).select_related(
        'farmacia_origen',
        'motorista',
        'validado_por',
    )

    context = {
        'periodo': periodo,
        'fecha_referencia': fecha_referencia.isoformat(),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'periodo_titulo': periodo_titulo,
        'pedidos': pedidos,
        'total_pedidos': pedidos.count(),
        'total_farmacias': pedidos.values('farmacia_origen').distinct().count(),
        'total_motoristas': pedidos.values('motorista').distinct().count(),
    }
    return render(request, 'app_movimientos/reportes.html', context)


def logout_view(request):
    """
    Cierra la sesión del usuario actual y lo redirige a la pantalla de login.
    """
    logout(request)
    return redirect('login')

# ==================== MANTENEDORES GENÉRICOS (MIXINS Y BASES) ====================
class CustomBaseListView(LoginRequiredMixin, ListView):
    """
    Clase base genérica para vistas de listado CRUD (Read).
    Inyecta automáticamente en el contexto el título plural del modelo y las URLs estándar de acción.
    """
    template_name = 'app_movimientos/mantenedor_list.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = self.model._meta.verbose_name_plural
        ctx['url_crear'] = f"{self.model._meta.model_name}_create"
        ctx['url_editar'] = f"{self.model._meta.model_name}_update"
        ctx['url_eliminar'] = f"{self.model._meta.model_name}_delete"
        return ctx

class CustomBaseCreateView(LoginRequiredMixin, CreateView):
    """
    Clase base genérica para vistas de creación de registros (Create).
    Configura el título, texto del botón y URL de cancelación de forma estandarizada.
    """
    template_name = 'app_movimientos/mantenedor_form.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f"Crear {self.model._meta.verbose_name}"
        ctx['btn_texto'] = "Guardar"
        ctx['url_cancelar'] = f"{self.model._meta.model_name}_list"
        return ctx

class CustomBaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    Clase base genérica para vistas de edición y modificación de registros (Update).
    """
    template_name = 'app_movimientos/mantenedor_form.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f"Editar {self.model._meta.verbose_name}"
        ctx['btn_texto'] = "Actualizar"
        ctx['url_cancelar'] = f"{self.model._meta.model_name}_list"
        return ctx

class CustomBaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    Clase base genérica para la confirmación de eliminación de registros (Delete).
    """
    template_name = 'app_movimientos/mantenedor_confirm_delete.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f"Eliminar {self.model._meta.verbose_name}"
        ctx['url_cancelar'] = f"{self.model._meta.model_name}_list"
        return ctx


def _catalogo_motoristas_por_farmacia():
    """
    Función auxiliar de consulta que genera un diccionario optimizado en memoria
    mapeando cada ID de farmacia con su lista de motoristas activos asignados.
    Utilizada para alimentar menús dependientes en la interfaz por AJAX/JavaScript.
    """
    catalogo = {}
    asignaciones = AsignacionMotorista.objects.filter(
        motorista__estado='ACTIVO',
    ).select_related('motorista').order_by('motorista__nombre_completo')
    for asignacion in asignaciones:
        catalogo.setdefault(str(asignacion.farmacia_id), []).append({
            'id': asignacion.motorista_id,
            'nombre': asignacion.motorista.nombre_completo,
            'rut': asignacion.motorista.rut,
        })
    return catalogo


# ==================== MANTENEDOR: DESPACHOS ====================
class MovimientoCreateView(CustomBaseCreateView):
    model = Movimiento
    form_class = MovimientoTipoForm
    success_url = reverse_lazy('movimientos_list')
    tipo_movimiento = 'DIRECTO'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tipo_movimiento'] = self.tipo_movimiento
        return kwargs

    def form_valid(self, form):
        form.instance.tipo_movimiento = self.tipo_movimiento
        if form.cleaned_data.get('validado'):
            form.instance.fecha_validacion = timezone.now()
            form.instance.validado_por = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tipo_etiqueta = dict(Movimiento.TIPO_CHOICES)[self.tipo_movimiento]
        ctx['titulo'] = f"Agregar movimiento {tipo_etiqueta.lower()}"
        ctx['tipo_movimiento'] = tipo_etiqueta
        ctx['url_cancelar'] = 'movimientos_list'
        ctx['motoristas_por_farmacia'] = _catalogo_motoristas_por_farmacia()
        ctx['mostrar_selector_motoristas'] = True
        return ctx

class MovimientoUpdateView(CustomBaseUpdateView):
    model = Movimiento
    form_class = MovimientoForm
    success_url = reverse_lazy('movimientos_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tipo_movimiento'] = self.get_object().tipo_movimiento
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.get_object().estado == 'ANULADO':
            return redirect('movimientos_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        estaba_validado = self.get_object().validado
        if form.cleaned_data.get('validado'):
            if not estaba_validado:
                form.instance.fecha_validacion = timezone.now()
                form.instance.validado_por = self.request.user
        else:
            form.instance.fecha_validacion = None
            form.instance.validado_por = None
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = "Modificar movimiento"
        ctx['url_cancelar'] = 'movimientos_list'
        ctx['motoristas_por_farmacia'] = _catalogo_motoristas_por_farmacia()
        ctx['mostrar_selector_motoristas'] = True
        return ctx


@login_required
def anular_movimiento_view(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    if movimiento.estado == 'ANULADO':
        return redirect('movimientos_list')

    form = AnularMovimientoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        movimiento.estado = 'ANULADO'
        movimiento.validado = False
        movimiento.fecha_validacion = None
        movimiento.validado_por = None
        movimiento.fecha_anulacion = timezone.now()
        movimiento.anulado_por = request.user
        movimiento.motivo_anulacion = form.cleaned_data['motivo_anulacion']
        movimiento.save(update_fields=[
            'estado',
            'validado',
            'fecha_validacion',
            'validado_por',
            'fecha_anulacion',
            'anulado_por',
            'motivo_anulacion',
        ])
        return redirect('movimientos_list')

    return render(request, 'app_movimientos/movimiento_anular.html', {
        'movimiento': movimiento,
        'form': form,
    })

# ==================== MANTENEDOR: FARMACIAS ====================
class FarmaciaListView(CustomBaseListView): model = Farmacia


class TerritorioContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['territorios'] = TERRITORIOS
        return context


class FarmaciaCreateView(TerritorioContextMixin, CustomBaseCreateView):
    model = Farmacia
    form_class = FarmaciaForm
    success_url = reverse_lazy('farmacia_list')


class FarmaciaUpdateView(TerritorioContextMixin, CustomBaseUpdateView):
    model = Farmacia
    form_class = FarmaciaForm
    success_url = reverse_lazy('farmacia_list')


class FarmaciaDeleteView(CustomBaseDeleteView): model = Farmacia; success_url = reverse_lazy('farmacia_list')

# ==================== MANTENEDOR: MOTORISTAS ====================
class MotoristaListView(CustomBaseListView):
    model = Motorista

    def get_queryset(self):
        queryset = super().get_queryset()
        self.busqueda = self.request.GET.get('q', '').strip()
        self.region = self.request.GET.get('region', '').strip()

        if self.busqueda:
            queryset = queryset.filter(
                Q(nombre_completo__icontains=self.busqueda)
                | Q(rut__icontains=self.busqueda)
            )

        regiones_validas = {valor for valor, _ in Farmacia.REGION_CHOICES}
        if self.region in regiones_validas:
            queryset = queryset.filter(region=self.region)
        else:
            self.region = ''

        return queryset.order_by('nombre_completo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mostrar_filtros_motorista'] = True
        context['busqueda'] = self.busqueda
        context['region_seleccionada'] = self.region
        context['regiones'] = Farmacia.REGION_CHOICES
        return context


class MotoristaCreateView(TerritorioContextMixin, CustomBaseCreateView):
    model = Motorista
    form_class = MotoristaForm
    success_url = reverse_lazy('motorista_list')


class MotoristaUpdateView(TerritorioContextMixin, CustomBaseUpdateView):
    model = Motorista
    form_class = MotoristaForm
    success_url = reverse_lazy('motorista_list')


class MotoristaDeleteView(CustomBaseDeleteView): model = Motorista; success_url = reverse_lazy('motorista_list')

# ==================== MANTENEDOR: USUARIOS ====================
class UsuarioSistemaListView(CustomBaseListView): model = UsuarioSistema
class UsuarioSistemaCreateView(CustomBaseCreateView): model = UsuarioSistema; form_class = UsuarioSistemaForm; success_url = reverse_lazy('usuariosistema_list')
class UsuarioSistemaUpdateView(CustomBaseUpdateView): model = UsuarioSistema; form_class = UsuarioSistemaForm; success_url = reverse_lazy('usuariosistema_list')
class UsuarioSistemaDeleteView(CustomBaseDeleteView): model = UsuarioSistema; success_url = reverse_lazy('usuariosistema_list')

# ==================== MANTENEDOR: MOTOS ====================
class MotoListView(CustomBaseListView):
    model = Moto

    def get_queryset(self):
        queryset = super().get_queryset().select_related('marca', 'modelo')
        self.busqueda = self.request.GET.get('q', '').strip()
        self.estado = self.request.GET.get('estado', '').strip()

        if self.busqueda:
            queryset = queryset.filter(
                Q(patente__icontains=self.busqueda)
                | Q(marca__nombre__icontains=self.busqueda)
                | Q(modelo__nombre__icontains=self.busqueda)
            )

        estados_validos = {valor for valor, _ in Moto.ESTADO_CHOICES}
        if self.estado in estados_validos:
            queryset = queryset.filter(estado=self.estado)
        else:
            self.estado = ''

        return queryset.order_by('patente')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mostrar_filtros_moto'] = True
        ctx['busqueda'] = self.busqueda
        ctx['estado_seleccionado'] = self.estado
        ctx['estados_moto'] = Moto.ESTADO_CHOICES
        return ctx

class MotoCatalogoMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalogo = {}
        modelos = ModeloMoto.objects.select_related('marca').order_by(
            'marca__nombre',
            'nombre',
        )
        for modelo in modelos:
            catalogo.setdefault(str(modelo.marca_id), []).append({
                'id': modelo.pk,
                'nombre': modelo.nombre,
            })
        context['catalogo_motos'] = catalogo
        return context


class MotoCreateView(MotoCatalogoMixin, CustomBaseCreateView):
    model = Moto
    form_class = MotoForm
    success_url = reverse_lazy('moto_list')


class MotoUpdateView(MotoCatalogoMixin, CustomBaseUpdateView):
    model = Moto
    form_class = MotoForm
    success_url = reverse_lazy('moto_list')


class MotoDeleteView(CustomBaseDeleteView): model = Moto; success_url = reverse_lazy('moto_list')

# ==================== ASIGNACIONES DE MOTORISTAS ====================
class AsignacionMotoristaListView(LoginRequiredMixin, ListView):
    model = AsignacionMotorista
    template_name = 'app_movimientos/asignaciones_list.html'
    context_object_name = 'asignaciones'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'motorista',
            'farmacia',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_motoristas'] = Motorista.objects.count()
        context['total_asignados'] = AsignacionMotorista.objects.count()
        context['total_sin_asignar'] = Motorista.objects.filter(
            asignacion_farmacia__isnull=True,
        ).count()
        context['total_farmacias'] = Farmacia.objects.count()
        return context


class AsignacionMotoristaCreateView(LoginRequiredMixin, CreateView):
    model = AsignacionMotorista
    form_class = AsignacionMotoristaForm
    template_name = 'app_movimientos/asignacion_form.html'
    success_url = reverse_lazy('asignacion_list')


class AsignacionMotoristaUpdateView(LoginRequiredMixin, UpdateView):
    model = AsignacionMotorista
    form_class = AsignacionMotoristaForm
    template_name = 'app_movimientos/asignacion_form.html'
    success_url = reverse_lazy('asignacion_list')


class AsignacionMotoristaDeleteView(LoginRequiredMixin, DeleteView):
    model = AsignacionMotorista
    template_name = 'app_movimientos/mantenedor_confirm_delete.html'
    success_url = reverse_lazy('asignacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Quitar asignación'
        context['url_cancelar'] = 'asignacion_list'
        return context


# ==================== MANTENEDOR: ASIGNACIONES ====================
class AsignacionTurnoListView(CustomBaseListView): model = AsignacionTurno
class AsignacionTurnoCreateView(CustomBaseCreateView): model = AsignacionTurno; form_class = AsignacionTurnoForm; success_url = reverse_lazy('asignacionturno_list')
class AsignacionTurnoUpdateView(CustomBaseUpdateView): model = AsignacionTurno; form_class = AsignacionTurnoForm; success_url = reverse_lazy('asignacionturno_list')
class AsignacionTurnoDeleteView(CustomBaseDeleteView): model = AsignacionTurno; success_url = reverse_lazy('asignacionturno_list')
