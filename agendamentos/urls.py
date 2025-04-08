from django.urls import path
from .views import (
    home,
    listar_barbeiros,
    calendario_com_token,
    criar_agendamento,
    horarios_ocupados,
    horarios_bloqueados,
    cancelar_agendamento,
    api_horarios,
    api_bloqueios
)

app_name = 'agendamentos'

urlpatterns = [
    path('', home, name='home'),

    path('barbeiros/', listar_barbeiros, name='listar_barbeiros'),

    path('calendario/<int:barbeiro_id>/', calendario_com_token, name='calendario_barbeiro'),

    path('api/agendamentos/', criar_agendamento, name='criar_agendamento'),
    path('api/horarios/<int:barbeiro_id>/', horarios_ocupados, name='horarios_ocupados'),
    path('api/bloqueios/<int:barbeiro_id>/', horarios_bloqueados, name='horarios_bloqueados'),

    path('api_horarios/<int:barbeiro_id>/', api_horarios, name='api_horarios'),
    path('api_bloqueios/<int:barbeiro_id>/', api_bloqueios, name='api_bloqueios'),

    path('cancelar-agendamento/<int:agendamento_id>/<uuid:token>/', cancelar_agendamento, name='cancelar_agendamento'),
]
