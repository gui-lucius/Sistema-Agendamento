from django.urls import path
from django.shortcuts import render
from .views import (
    criar_agendamento,
    horarios_ocupados,
    horarios_bloqueados,
    home
)

app_name = 'agendamentos'

def exibir_calendario(request):
    return render(request, 'calendario.html')

urlpatterns = [
    path('', home, name='home'),
    path('calendario/', exibir_calendario, name='calendario'),

    path('api/agendamentos/', criar_agendamento, name='criar_agendamento'),
    path('api/horarios/', horarios_ocupados, name='horarios_ocupados'),
    path('api/bloqueios/', horarios_bloqueados, name='horarios_bloqueados'),
]
