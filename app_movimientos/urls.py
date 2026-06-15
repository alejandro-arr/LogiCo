from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='app_movimientos/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('movimientos/', views.movimientos_list_view, name='movimientos_list'),
    path('movimientos/crear/', views.MovimientoCreateView.as_view(), name='movimiento_create'),
    path('movimientos/crear/directo/', views.MovimientoCreateView.as_view(tipo_movimiento='DIRECTO'), name='movimiento_directo_create'),
    path('movimientos/crear/receta/', views.MovimientoCreateView.as_view(tipo_movimiento='RECETA'), name='movimiento_receta_create'),
    path('movimientos/crear/traslado/', views.MovimientoCreateView.as_view(tipo_movimiento='TRASLADO'), name='movimiento_traslado_create'),
    path('movimientos/crear/reenvio/', views.MovimientoCreateView.as_view(tipo_movimiento='REENVIO'), name='movimiento_reenvio_create'),
    path('movimientos/editar/<int:pk>/', views.MovimientoUpdateView.as_view(), name='movimiento_update'),
    path('movimientos/anular/<int:pk>/', views.anular_movimiento_view, name='movimiento_anular'),
    path('reportes/', views.reportes_view, name='reportes'),

    # Rutas Farmacia
    path('farmacias/', views.FarmaciaListView.as_view(), name='farmacia_list'),
    path('farmacias/crear/', views.FarmaciaCreateView.as_view(), name='farmacia_create'),
    path('farmacias/editar/<int:pk>/', views.FarmaciaUpdateView.as_view(), name='farmacia_update'),
    path('farmacias/eliminar/<int:pk>/', views.FarmaciaDeleteView.as_view(), name='farmacia_delete'),

    # Rutas Motorista
    path('motoristas/', views.MotoristaListView.as_view(), name='motorista_list'),
    path('motoristas/crear/', views.MotoristaCreateView.as_view(), name='motorista_create'),
    path('motoristas/editar/<int:pk>/', views.MotoristaUpdateView.as_view(), name='motorista_update'),
    path('motoristas/eliminar/<int:pk>/', views.MotoristaDeleteView.as_view(), name='motorista_delete'),

    # Rutas Usuarios
    path('usuarios/', views.UsuarioSistemaListView.as_view(), name='usuariosistema_list'),
    path('usuarios/crear/', views.UsuarioSistemaCreateView.as_view(), name='usuariosistema_create'),
    path('usuarios/editar/<int:pk>/', views.UsuarioSistemaUpdateView.as_view(), name='usuariosistema_update'),
    path('usuarios/eliminar/<int:pk>/', views.UsuarioSistemaDeleteView.as_view(), name='usuariosistema_delete'),

    # Rutas Moto
    path('motos/', views.MotoListView.as_view(), name='moto_list'),
    path('motos/crear/', views.MotoCreateView.as_view(), name='moto_create'),
    path('motos/editar/<int:pk>/', views.MotoUpdateView.as_view(), name='moto_update'),
    path('motos/eliminar/<int:pk>/', views.MotoDeleteView.as_view(), name='moto_delete'),

    # Asignaciones actuales de motoristas a farmacias
    path('asignaciones/', views.AsignacionMotoristaListView.as_view(), name='asignacion_list'),
    path('asignaciones/crear/', views.AsignacionMotoristaCreateView.as_view(), name='asignacion_create'),
    path('asignaciones/editar/<int:pk>/', views.AsignacionMotoristaUpdateView.as_view(), name='asignacion_update'),
    path('asignaciones/eliminar/<int:pk>/', views.AsignacionMotoristaDeleteView.as_view(), name='asignacion_delete'),

    # Rutas AsignacionTurno
    path('turnos/', views.AsignacionTurnoListView.as_view(), name='asignacionturno_list'),
    path('turnos/crear/', views.AsignacionTurnoCreateView.as_view(), name='asignacionturno_create'),
    path('turnos/editar/<int:pk>/', views.AsignacionTurnoUpdateView.as_view(), name='asignacionturno_update'),
    path('turnos/eliminar/<int:pk>/', views.AsignacionTurnoDeleteView.as_view(), name='asignacionturno_delete'),
]
