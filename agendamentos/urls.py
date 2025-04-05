from django.urls import path
from .views import (
    criar_agendamento,
    horarios_ocupados,
    horarios_bloqueados,
    home,
    calendario_com_token,
    listar_barbeiros  # ⬅️ IMPORTA a nova view
)

app_name = 'agendamentos'

urlpatterns = [
    path('', home, name='home'),
    
    # ✅ ROTA PARA LISTAR TODOS OS BARBEIROS
    path('barbeiros/', listar_barbeiros, name='listar_barbeiros'),

    # ✅ ROTA PARA AGENDA DE UM BARBEIRO ESPECÍFICO
    path('calendario/<int:barbeiro_id>/', calendario_com_token, name='calendario_barbeiro'),

    # APIs
    path('api/agendamentos/', criar_agendamento, name='criar_agendamento'),
    path('api/horarios/<int:barbeiro_id>/', horarios_ocupados, name='horarios_ocupados'),
    path('api/bloqueios/<int:barbeiro_id>/', horarios_bloqueados, name='horarios_bloqueados'),

]
