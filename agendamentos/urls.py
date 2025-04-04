from django.urls import path
from .views import (
    criar_agendamento,
    horarios_ocupados,
    horarios_bloqueados,
    home,
    calendario_com_token  
)

app_name = 'agendamentos'

urlpatterns = [
    path('', home, name='home'),
    path('calendario/', calendario_com_token, name='calendario'),  

    path('api/agendamentos/', criar_agendamento, name='criar_agendamento'),
    path('api/horarios/', horarios_ocupados, name='horarios_ocupados'),
    path('api/bloqueios/', horarios_bloqueados, name='horarios_bloqueados'),
]
