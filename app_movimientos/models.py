"""
Módulo de Modelos de Datos (ORM Django) - Logística y Despacho de Farmacias.

Este módulo define la estructura de la base de datos y la lógica de negocio de las entidades
principales del sistema: Farmacias, Motoristas, Motos, Turnos Operativos y Movimientos (despachos).

Buenas prácticas aplicadas:
- Normalización de base de datos hasta la 3ª Forma Normal (evita redundancia de datos).
- Uso de tablas transaccionales intermedias (AsignacionTurno) en lugar de acoplamiento directo.
- Validaciones a nivel de modelo mediante el método clean() para mantener la integridad de las reglas de negocio.
- Uso de on_delete=PROTECT en relaciones críticas para prevenir el borrado accidental de registros con historial operativo.
"""

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string


def generar_codigo_movimiento():
    """
    Genera un código alfanumérico único y aleatorio para identificar un movimiento de despacho.

    Returns:
        str: Código en formato 'MOV-XXXXXXXX' (ej. MOV-4829AFE1).
    """
    return f"MOV-{get_random_string(8).upper()}"


def limpiar_rut(rut):
    """
    Normaliza una cadena que representa un RUT chileno eliminando puntos, guiones y espacios en blanco.

    Args:
        rut (str): RUT en cualquier formato (ej. ' 12.345.678-k ').

    Returns:
        str: RUT limpio y en mayúsculas (ej. '12345678K').
    """
    return (rut or '').strip().upper().replace('.', '').replace('-', '')


def calcular_digito_verificador_rut(cuerpo):
    """
    Calcula el Dígito Verificador (DV) de un RUT chileno utilizando el algoritmo de Módulo 11.

    Args:
        cuerpo (str): Parte numérica del RUT sin dígito verificador.

    Returns:
        str: Dígito verificador calculado ('0'-'9' o 'K').
    """
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resultado = 11 - (suma % 11)
    if resultado == 11:
        return '0'
    if resultado == 10:
        return 'K'
    return str(resultado)


def rut_chileno_valido(rut):
    """
    Valida integralmente si un RUT chileno es sintáctico y matemáticamente correcto.

    Verifica formato admitido (dígitos, puntos, guión y K), longitud mínima, cuerpo numérico,
    que no sea cero y que el dígito verificador coincida con el cálculo de Módulo 11.

    Args:
        rut (str): RUT a evaluar.

    Returns:
        bool: True si el RUT es válido, False en caso contrario.
    """
    rut_texto = (rut or '').strip().upper()
    if not rut_texto or not re.fullmatch(r'[\d.\-K]+', rut_texto):
        return False

    rut_limpio = limpiar_rut(rut_texto)
    if len(rut_limpio) < 2:
        return False

    cuerpo = rut_limpio[:-1]
    digito_verificador = rut_limpio[-1]
    if not cuerpo.isdigit() or digito_verificador not in '0123456789K':
        return False
    if int(cuerpo) == 0:
        return False

    return calcular_digito_verificador_rut(cuerpo) == digito_verificador


def formatear_rut(rut):
    """
    Aplica el formato estándar chileno con puntos y guión a una cadena de RUT válido.

    Args:
        rut (str): RUT en cualquier formato.

    Returns:
        str: RUT formateado como 'XX.XXX.XXX-Y'.
    """
    rut_limpio = limpiar_rut(rut)
    cuerpo = str(int(rut_limpio[:-1]))
    digito_verificador = rut_limpio[-1]
    cuerpo_formateado = f"{int(cuerpo):,}".replace(',', '.')
    return f"{cuerpo_formateado}-{digito_verificador}"

class Farmacia(models.Model):
    """
    Entidad que representa un local físico o sucursal de farmacia.

    Almacena los datos de contacto, ubicación administrativa (Región, Provincia, Comuna)
    y actúa como punto de origen o destino para los despachos y turnos operativos.
    """
    REGION_CHOICES = [
        ('ARICA_PARINACOTA', 'Región de Arica y Parinacota'),
        ('TARAPACA', 'Región de Tarapacá'),
        ('ANTOFAGASTA', 'Región de Antofagasta'),
        ('ATACAMA', 'Región de Atacama'),
        ('COQUIMBO', 'Región de Coquimbo'),
        ('VALPARAISO', 'Región de Valparaíso'),
        ('METROPOLITANA', 'Región Metropolitana de Santiago'),
        ('OHIGGINS', "Región del Libertador General Bernardo O'Higgins"),
        ('MAULE', 'Región del Maule'),
        ('NUBLE', 'Región de Ñuble'),
        ('BIOBIO', 'Región del Biobío'),
        ('ARAUCANIA', 'Región de La Araucanía'),
        ('LOS_RIOS', 'Región de Los Ríos'),
        ('LOS_LAGOS', 'Región de Los Lagos'),
        ('AYSEN', 'Región de Aysén del General Carlos Ibáñez del Campo'),
        ('MAGALLANES', 'Región de Magallanes y de la Antártica Chilena'),
    ]

    nombre_local = models.CharField(max_length=100, verbose_name="Nombre del Local")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    encargado = models.CharField(max_length=100, verbose_name="Encargado")
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        verbose_name="Región",
    )
    provincia = models.CharField(max_length=100, default='', verbose_name="Provincia")
    comuna = models.CharField(max_length=100, default='', verbose_name="Comuna")

    class Meta:
        verbose_name = "Farmacia"
        verbose_name_plural = "Farmacias"
        ordering = ['nombre_local']

    def __str__(self):
        region = self.get_region_display() if self.region else "Región pendiente"
        return f"{self.nombre_local} - {region}"


class Motorista(models.Model):
    """
    Entidad que representa a un conductor o repartidor (motorista) de la flota.

    Incluye control de estado (Activo/Inactivo), datos personales y ubicación de residencia.
    Aplica validación obligatoria de RUT chileno en su método clean() para mantener
    la integridad y unicidad del personal.
    """
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre_completo = models.CharField(max_length=150, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ACTIVO', verbose_name="Estado")
    region = models.CharField(
        max_length=20,
        choices=Farmacia.REGION_CHOICES,
        default='',
        verbose_name="Región",
    )
    provincia = models.CharField(max_length=100, default='', verbose_name="Provincia")
    comuna = models.CharField(max_length=100, default='', verbose_name="Comuna")

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"

    def __str__(self):
        ubicacion = self.comuna or self.get_region_display() or "Ubicación pendiente"
        return f"{self.rut} - {self.nombre_completo} ({ubicacion})"

    def clean(self):
        super().clean()
        if self.rut and not rut_chileno_valido(self.rut):
            raise ValidationError({
                'rut': 'Ingrese un RUT chileno válido.',
            })
        if self.rut:
            self.rut = formatear_rut(self.rut)


class UsuarioSistema(models.Model):
    """
    Entidad que representa a los usuarios administrativos del sistema de logística.

    Permite clasificar al personal según roles jerárquicos (Admin, Gerente, Supervisor, etc.)
    para control de acceso, auditoría y validación/anulación de pedidos.
    """
    ROL_CHOICES = [
        ('ADMIN', 'Admin'),
        ('GERENTE', 'Gerente'),
        ('SUPERVISOR', 'Supervisor'),
        ('MOTORISTA', 'Motorista'),
        ('GENERICO', 'Usuario generico'),
    ]

    nombre_completo = models.CharField(max_length=150, verbose_name="Nombre completo")
    correo = models.EmailField(max_length=150, unique=True, verbose_name="Correo")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Telefono")
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='GENERICO', verbose_name="Rol")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombre_completo']

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre_completo} - {self.get_rol_display()} ({estado})"


class MarcaMoto(models.Model):
    """
    Catálogo de marcas de motocicletas (ej. Honda, Yamaha, Suzuki).

    Sirve para normalizar y estructurar la flota de vehículos sin strings arbitrarios.
    """
    nombre = models.CharField(max_length=80, unique=True, verbose_name="Marca")

    class Meta:
        verbose_name = "Marca de moto"
        verbose_name_plural = "Marcas de moto"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ModeloMoto(models.Model):
    """
    Catálogo de modelos específicos de motocicletas asociados a una Marca.

    Implementa una restricción de unicidad (UniqueConstraint) para evitar duplicar
    el mismo nombre de modelo dentro de la misma marca.
    """
    marca = models.ForeignKey(
        MarcaMoto,
        on_delete=models.CASCADE,
        related_name='modelos',
        verbose_name="Marca",
    )
    nombre = models.CharField(max_length=100, verbose_name="Modelo")

    class Meta:
        verbose_name = "Modelo de moto"
        verbose_name_plural = "Modelos de moto"
        ordering = ['marca__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['marca', 'nombre'],
                name='modelo_moto_unico_por_marca',
            ),
        ]

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"


class Moto(models.Model):
    """
    Entidad que representa una unidad física dentro de la flota de motocicletas.

    Identificada unívocamente por su patente. Contiene su estado operativo (Disponible
    o En Mantención). Su método clean() garantiza que el modelo pertenezca a la marca seleccionada.
    """
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('MANTENCION', 'En Mantención'),
    ]

    patente = models.CharField(max_length=10, unique=True, verbose_name="Patente")
    marca = models.ForeignKey(
        MarcaMoto,
        on_delete=models.PROTECT,
        related_name='motos',
        verbose_name="Marca",
    )
    modelo = models.ForeignKey(
        ModeloMoto,
        on_delete=models.PROTECT,
        related_name='motos',
        verbose_name="Modelo",
    )
    anio = models.IntegerField(verbose_name="Año")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='DISPONIBLE', verbose_name="Estado")

    class Meta:
        verbose_name = "Moto"
        verbose_name_plural = "Motos"

    def __str__(self):
        return f"{self.patente} - {self.marca.nombre} {self.modelo.nombre}"

    def clean(self):
        super().clean()
        if self.marca_id and self.modelo_id and self.modelo.marca_id != self.marca_id:
            raise ValidationError({
                'modelo': 'El modelo seleccionado no pertenece a la marca indicada.',
            })


class AsignacionMotorista(models.Model):
    """
    Entidad que registra la vinculación base actual entre un Motorista y una Farmacia.

    Al ser OneToOneField con Motorista, garantiza que un motorista solo tenga una farmacia base
    asignada a la vez, facilitando el filtrado en la creación de turnos y despachos directos.
    """
    motorista = models.OneToOneField(
        Motorista,
        on_delete=models.CASCADE,
        related_name='asignacion_farmacia',
        verbose_name="Motorista",
    )
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.PROTECT,
        related_name='motoristas_asignados',
        verbose_name="Farmacia",
    )
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de asignación",
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Asignación de motorista"
        verbose_name_plural = "Asignaciones"
        ordering = ['farmacia__nombre_local', 'motorista__nombre_completo']

    def __str__(self):
        return f"{self.motorista.nombre_completo} → {self.farmacia.nombre_local}"


class AsignacionTurno(models.Model):
    """
    MODELO CENTRAL: Asignación de Turno.
    Justificación para tu defensa: 
    En lugar de colocar llaves foráneas (ForeignKeys) directamente en la Moto o en el Motorista apuntando
    a una Farmacia, se crea esta tabla transaccional/intermedia. 
    ¿Por qué? Porque en logística un Motorista no es "dueño" de una moto ni pertenece a una Farmacia 
    para siempre. Esta tabla nos permite registrar el "Historial Operativo": saber exactamente qué Motorista, 
    manejó qué Moto, para qué Farmacia, y en qué fecha exacta. También permite cubrir limpiamente 
    el caso de uso de "Reemplazos" sin romper la estructura de datos.
    """
    farmacia = models.ForeignKey(Farmacia, on_delete=models.PROTECT, related_name='asignaciones', verbose_name="Farmacia")
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, related_name='asignaciones', verbose_name="Motorista")
    moto = models.ForeignKey(Moto, on_delete=models.PROTECT, related_name='asignaciones', verbose_name="Moto")
    fecha = models.DateField(verbose_name="Fecha de Asignación")
    es_reemplazo = models.BooleanField(default=False, verbose_name="¿Es reemplazo?")
    
    # Campo opcional sugerido: En caso de ser reemplazo, podríamos dejar una nota del motivo
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Asignación de Turno"
        verbose_name_plural = "Asignaciones de Turno"
        # Garantizamos que un motorista no pueda estar asignado a dos lugares el mismo día
        unique_together = ('motorista', 'fecha')

    def __str__(self):
        tipo = "REEMPLAZO" if self.es_reemplazo else "TITULAR"
        return f"{self.fecha} | {self.farmacia.nombre_local} | {self.motorista.nombre_completo} [{tipo}]"


class Movimiento(models.Model):
    """
    MODELO DE DESPACHO: Movimiento.
    Justificación para tu defensa:
    Este modelo representa la acción física del delivery. En lugar de relacionarlo directamente 
    con Motorista, Moto y Farmacia (lo que generaría redundancia de datos), lo relacionamos 
    únicamente con la 'AsignacionTurno'. Por transitividad, al saber el turno, el sistema sabe 
    inmediatamente desde qué farmacia salió el pedido, qué moto se usó y quién es el conductor. 
    Esto hace que la base de datos sea normalizada, escalable y evita anomalías en los datos.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_RUTA', 'En Ruta'),
        ('ENTREGADO', 'Entregado'),
        ('FALLIDO', 'Fallido'),
        ('ANULADO', 'Anulado'),
    ]

    TIPO_CHOICES = [
        ('DIRECTO', 'Directo'),
        ('RECETA', 'Con Receta'),
        ('TRASLADO', 'Traslado entre locales'),
        ('REENVIO', 'Reenvío'),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True,
        default=generar_codigo_movimiento,
        verbose_name="Código de movimiento",
    )
    farmacia_origen = models.ForeignKey(
        Farmacia,
        on_delete=models.PROTECT,
        related_name='movimientos_origen',
        verbose_name="Origen del movimiento",
    )
    farmacia_destino = models.ForeignKey(
        Farmacia,
        on_delete=models.PROTECT,
        related_name='movimientos_destino',
        blank=True,
        null=True,
        verbose_name="Farmacia de destino",
    )
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.PROTECT,
        related_name='movimientos',
        blank=True,
        null=True,
        verbose_name="Motorista",
    )
    asignacion_turno = models.ForeignKey(
        AsignacionTurno,
        on_delete=models.PROTECT,
        related_name='movimientos',
        blank=True,
        null=True,
        verbose_name="Turno operativo",
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora del Registro")
    direccion_destino = models.CharField(max_length=255, verbose_name="Dirección de Destino")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado del Despacho")
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='DIRECTO', verbose_name="Tipo de Movimiento")
    validado = models.BooleanField(default=False, verbose_name="Pedido validado")
    fecha_validacion = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de validación")
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='movimientos_validados',
        blank=True,
        null=True,
        verbose_name="Validado por",
    )
    fecha_anulacion = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de anulación")
    anulado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='movimientos_anulados',
        blank=True,
        null=True,
        verbose_name="Anulado por",
    )
    motivo_anulacion = models.TextField(blank=True, verbose_name="Motivo de anulación")

    class Meta:
        verbose_name = "Movimiento de Despacho"
        verbose_name_plural = "Movimientos de Despacho"
        ordering = ['-fecha_hora'] # Los más recientes primero

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} a {self.direccion_destino} - {self.get_estado_display()}"

    def clean(self):
        super().clean()
        if self.tipo_movimiento == 'TRASLADO':
            if not self.farmacia_destino_id:
                raise ValidationError({
                    'farmacia_destino': 'Debe seleccionar la farmacia de destino.',
                })
            if self.farmacia_destino_id == self.farmacia_origen_id:
                raise ValidationError({
                    'farmacia_destino': 'La farmacia de destino debe ser distinta del origen.',
                })
        elif self.farmacia_destino_id:
            raise ValidationError({
                'farmacia_destino': 'La farmacia de destino solo corresponde a traslados.',
            })
        if (
            self.asignacion_turno_id
            and self.farmacia_origen_id
            and self.asignacion_turno.farmacia_id != self.farmacia_origen_id
        ):
            raise ValidationError({
                'farmacia_origen': 'La farmacia de origen no coincide con el turno operativo.',
            })
        if (
            self.asignacion_turno_id
            and self.motorista_id
            and self.asignacion_turno.motorista_id != self.motorista_id
        ):
            raise ValidationError({
                'motorista': 'El motorista no coincide con el turno operativo.',
            })
        if self.validado and self.estado != 'ENTREGADO':
            raise ValidationError({
                'validado': 'Solo se puede validar un pedido con estado Entregado.',
            })
