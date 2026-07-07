from django.contrib import admin
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

# Registramos los modelos básicos
admin.site.register(Farmacia)
admin.site.register(Motorista)
admin.site.register(UsuarioSistema)
admin.site.register(Moto)
admin.site.register(MarcaMoto)
admin.site.register(ModeloMoto)
admin.site.register(AsignacionTurno)
admin.site.register(AsignacionMotorista)
admin.site.register(Movimiento)
