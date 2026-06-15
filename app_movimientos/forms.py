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

# Mixin personalizado para aplicar clases Bootstrap a todos los formularios sin librerías externas
class BootstrapStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

class FarmaciaForm(BootstrapStyleMixin, forms.ModelForm):
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

class UsuarioSistemaForm(BootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = UsuarioSistema
        fields = ['nombre_completo', 'correo', 'telefono', 'rol', 'activo']

class MotoForm(BootstrapStyleMixin, forms.ModelForm):
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
    class Meta:
        model = AsignacionTurno
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

class MovimientoForm(BootstrapStyleMixin, forms.ModelForm):
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
    motivo_anulacion = forms.CharField(
        label='Motivo de anulación',
        widget=forms.Textarea(attrs={'rows': 4}),
        min_length=5,
    )
