"""
Módulo de Formularios y Validación de Interfaz (Forms & FormMixins).

Define los formularios de Django para la captura de datos y validación de negocio antes
de persistir en la base de datos. Implementa menús desplegables en cascada (AJAX/dependientes)
para la división territorial y filtrado dinámico de motoristas según su farmacia de asignación.

Buenas prácticas aplicadas:
- Principio DRY (Don't Repeat Yourself): Uso del mixin BootstrapStyleMixin para estilizar automáticamente todos los widgets con clases CSS sin acoplamiento manual en HTML.
- Validación multicapa: Validaciones cruzadas en el método clean() (ej. coherencia de comunas con provincias y validación de turnos operativos).
- Consultas optimizadas en inicializadores (__init__) para acotar las opciones mostradas al usuario según el contexto operativo.
"""

from django import forms
from django.db.models import Q
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
from .territorios import comunas_de, provincias_de, ubicacion_valida

class BootstrapStyleMixin:
    """
    Mixin arquitectónico para inyectar estilos de Bootstrap 5 en los widgets de Django.

    recorre dinámicamente los campos del formulario durante la instanciación y asigna 'form-control'
    o 'form-check-input', permitiendo un mantenimiento limpio y evitando dependencias pesadas como django-widget-tweaks.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

class FarmaciaForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario para la gestión de sucursales de Farmacia.

    Implementa lógica de menús desplegables dependientes para Región → Provincia → Comuna.
    Al inicializarse, carga las provincias y comunas correspondientes a la región seleccionada
    en los datos enviados (POST) o en la instancia existente (al editar).
    """
    provincia = forms.ChoiceField(
        choices=[('', 'Seleccione una región primero')],
        label='Provincia',
    )
    comuna = forms.ChoiceField(
        choices=[('', 'Seleccione una provincia primero')],
        label='Comuna',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region = self.data.get('region') or getattr(self.instance, 'region', '')
        provincia = self.data.get('provincia') or getattr(self.instance, 'provincia', '')

        if region:
            self.fields['provincia'].choices = [
                ('', 'Seleccione una provincia'),
                *((valor, valor) for valor in provincias_de(region)),
            ]
        if region and provincia:
            self.fields['comuna'].choices = [
                ('', 'Seleccione una comuna'),
                *((valor, valor) for valor in comunas_de(region, provincia)),
            ]

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        provincia = cleaned_data.get('provincia')
        comuna = cleaned_data.get('comuna')
        if region and provincia and comuna and not ubicacion_valida(region, provincia, comuna):
            raise forms.ValidationError(
                'La provincia y la comuna no corresponden a la región seleccionada.'
            )
        return cleaned_data

    class Meta:
        model = Farmacia
        fields = [
            'nombre_local',
            'direccion',
            'telefono',
            'encargado',
            'region',
            'provincia',
            'comuna',
        ]

class MotoristaForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario para el registro y modificación de Motoristas.

    Al igual que FarmaciaForm, gestiona dropdowns dependientes de ubicación territorial
    y proporciona textos de ayuda para guiar el ingreso correcto del RUT chileno.
    """
    provincia = forms.ChoiceField(
        choices=[('', 'Seleccione una región primero')],
        label='Provincia',
    )
    comuna = forms.ChoiceField(
        choices=[('', 'Seleccione una provincia primero')],
        label='Comuna',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        region = self.data.get('region') or getattr(self.instance, 'region', '')
        provincia = self.data.get('provincia') or getattr(self.instance, 'provincia', '')

        if region:
            self.fields['provincia'].choices = [
                ('', 'Seleccione una provincia'),
                *((valor, valor) for valor in provincias_de(region)),
            ]
        if region and provincia:
            self.fields['comuna'].choices = [
                ('', 'Seleccione una comuna'),
                *((valor, valor) for valor in comunas_de(region, provincia)),
            ]

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        provincia = cleaned_data.get('provincia')
        comuna = cleaned_data.get('comuna')
        if region and provincia and comuna and not ubicacion_valida(region, provincia, comuna):
            raise forms.ValidationError(
                'La provincia y la comuna no corresponden a la región seleccionada.'
            )
        return cleaned_data

    class Meta:
        model = Motorista
        fields = [
            'rut',
            'nombre_completo',
            'telefono',
            'estado',
            'region',
            'provincia',
            'comuna',
        ]
        help_texts = {
            'rut': 'Ingresa el RUT con dígito verificador. Ejemplo: 12.345.678-5 o 12345678-5.',
        }

class UsuarioSistemaForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario para la administración de usuarios del sistema y asignación de roles.
    """
    class Meta:
        model = UsuarioSistema
        fields = ['nombre_completo', 'correo', 'telefono', 'rol', 'activo']

class MotoForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario para la gestión del inventario de Motocicletas.

    Filtra dinámicamente el campo 'modelo' para que únicamente muestre los modelos
    pertenecientes a la 'marca' seleccionada, previniendo incoherencias vehiculares.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['marca'].queryset = MarcaMoto.objects.order_by('nombre')
        self.fields['modelo'].queryset = ModeloMoto.objects.none()
        self.fields['modelo'].label_from_instance = lambda modelo: modelo.nombre

        marca_id = self.data.get('marca') or getattr(self.instance, 'marca_id', None)
        try:
            marca_id = int(marca_id)
        except (TypeError, ValueError):
            marca_id = None

        if marca_id:
            self.fields['modelo'].queryset = ModeloMoto.objects.filter(
                marca_id=marca_id,
            ).select_related('marca').order_by('nombre')

    class Meta:
        model = Moto
        fields = '__all__'


class AsignacionMotoristaForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario para vincular un Motorista a una Farmacia base.

    En la creación (cuando no hay instancia previa), filtra el queryset para mostrar
    exclusivamente a los motoristas que no tienen una farmacia base asignada actualmente.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        motoristas = Motorista.objects.order_by('nombre_completo')
        if not self.instance.pk:
            motoristas = motoristas.filter(asignacion_farmacia__isnull=True)
        self.fields['motorista'].queryset = motoristas
        self.fields['farmacia'].queryset = Farmacia.objects.order_by('nombre_local')

    class Meta:
        model = AsignacionMotorista
        fields = ['motorista', 'farmacia', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Información adicional sobre la asignación (opcional)',
            }),
        }


class AsignacionTurnoForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario transaccional para la creación de Turnos Operativos diarios.
    """
    class Meta:
        model = AsignacionTurno
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

class MovimientoForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Formulario principal para el registro y modificación de Despachos (Movimientos).

    Controla reglas complejas:
    - Oculta o muestra la 'farmacia_destino' dependiendo de si es un TRASLADO entre locales.
    - Filtra el listado de motoristas seleccionables para mostrar únicamente a aquellos
      que están activos y asignados a la 'farmacia_origen'.
    """
    def __init__(self, *args, tipo_movimiento=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tipo_movimiento:
            self.instance.tipo_movimiento = tipo_movimiento
        self.tipo_movimiento = tipo_movimiento or self.instance.tipo_movimiento
        if self.tipo_movimiento != 'TRASLADO':
            self.fields.pop('farmacia_destino', None)
        self._configurar_motoristas()
        self.fields['estado'].choices = [
            choice for choice in Movimiento.ESTADO_CHOICES if choice[0] != 'ANULADO'
        ]

    def _configurar_motoristas(self):
        farmacia_id = self.data.get('farmacia_origen') or getattr(
            self.instance,
            'farmacia_origen_id',
            None,
        )
        motorista_id = self.data.get('motorista')
        queryset = Motorista.objects.filter(
            estado='ACTIVO',
            asignacion_farmacia__farmacia_id=farmacia_id,
        ).order_by('nombre_completo')
        if motorista_id or self.instance.motorista_id:
            motorista_id = motorista_id or self.instance.motorista_id
            queryset = Motorista.objects.filter(
                Q(pk=motorista_id)
                | Q(
                    estado='ACTIVO',
                    asignacion_farmacia__farmacia_id=farmacia_id,
                )
            ).distinct().order_by('nombre_completo')
        self.fields['motorista'].queryset = queryset
        self.fields['motorista'].required = True
        self.fields['motorista'].help_text = (
            'Se muestran los motoristas activos asignados a la farmacia de origen.'
        )

    def clean(self):
        cleaned_data = super().clean()
        farmacia = cleaned_data.get('farmacia_origen')
        motorista = cleaned_data.get('motorista')
        if (
            farmacia
            and motorista
            and not AsignacionMotorista.objects.filter(
                farmacia=farmacia,
                motorista=motorista,
            ).exists()
        ):
            self.add_error(
                'motorista',
                'El motorista seleccionado no está asignado a la farmacia de origen.',
            )
        return cleaned_data

    class Meta:
        model = Movimiento
        fields = [
            'codigo',
            'farmacia_origen',
            'farmacia_destino',
            'motorista',
            'direccion_destino',
            'observaciones',
            'estado',
            'tipo_movimiento',
            'validado',
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Información adicional del movimiento (opcional)',
            }),
        }
        help_texts = {
            'validado': 'Solo puede marcarse cuando el estado del despacho sea Entregado.',
        }


class MovimientoTipoForm(MovimientoForm):
    """
    Subclase de MovimientoForm adaptada para la creación rápida de despachos según su tipo.
    Oculta campos de control interno para simplificar la vista del operador.
    """
    class Meta:
        model = Movimiento
        fields = [
            'codigo',
            'farmacia_origen',
            'farmacia_destino',
            'motorista',
            'direccion_destino',
            'observaciones',
            'estado',
            'validado',
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Información adicional del movimiento (opcional)',
            }),
        }
        help_texts = {
            'validado': 'Solo puede marcarse cuando el estado del despacho sea Entregado.',
        }


class AnularMovimientoForm(BootstrapStyleMixin, forms.Form):
    """
    Formulario independiente para la anulación justificada de un despacho.
    Exige un motivo con longitud mínima para asegurar la trazabilidad en auditorías.
    """
    motivo_anulacion = forms.CharField(
        label='Motivo de anulación',
        widget=forms.Textarea(attrs={'rows': 4}),
        min_length=5,
    )
