from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dateutil import parser
from datetime import timedelta
from django.utils.timezone import make_naive, is_aware  # 👈 IMPORTANTE AQUI
from .models import Agendamento, HorarioBloqueado


# Página inicial
def home(request):
    return render(request, 'index.html')


# Utilitário de envio de e-mail
def notificar_agendamento(nome_cliente, data_horario):
    try:
        send_mail(
            'Novo Agendamento Pendente',
            f"Você tem uma nova solicitação de agendamento de {nome_cliente} no horário {data_horario}.\n\n"
            "Por favor, verifique o painel administrativo.",
            settings.EMAIL_REMETENTE,
            [settings.EMAIL_DESTINO],
            fail_silently=False
        )
    except Exception as e:
        print(f"[ERRO EMAIL] Não foi possível enviar notificação: {e}")


# Criar agendamento via POST
@api_view(['POST'])
def criar_agendamento(request):
    try:
        dados = request.data
        nome = dados.get('nome_cliente')
        email = dados.get('email_cliente')
        data = dados.get('data_horario_reserva')

        # Validações básicas
        if not all([nome, email, data]):
            return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'erro': 'E-mail inválido.'}, status=400)

        try:
            data = parser.parse(data)
            if is_aware(data):  # 👈 VERIFICA SE A DATA TEM TIMEZONE
                data = make_naive(data)  # 👈 REMOVE O TIMEZONE PRA EVITAR ERRO NO SQLITE
        except ValueError:
            return JsonResponse({'erro': 'Data/Horário inválido.'}, status=400)

        # Cria o agendamento
        agendamento = Agendamento.objects.create(
            nome_cliente=nome,
            email_cliente=email,
            data_horario_reserva=data,
            status='pendente'
        )

        notificar_agendamento(nome, data)

        return JsonResponse({'mensagem': 'Agendamento criado com sucesso!', 'id': agendamento.id}, status=201)

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao criar agendamento: {e}")
        return JsonResponse({'erro': 'Erro inesperado ao criar agendamento.'}, status=500)


# Buscar horários ocupados (usado pelo calendário)
@api_view(['GET'])
def horarios_ocupados(request):
    try:
        horarios = Agendamento.objects.filter(status__in=['pendente', 'aceito']).values(
            'data_horario_reserva', 'status'
        )
        return Response(list(horarios))
    except Exception as e:
        print(f"[ERRO] Falha ao buscar horários ocupados: {e}")
        return Response({'erro': 'Erro ao buscar horários ocupados.'}, status=500)


# Buscar horários bloqueados (ex: manutenção, folga)
@api_view(['GET'])
def horarios_bloqueados(request):
    try:
        bloqueios = HorarioBloqueado.objects.all().values('data_horario')
        return Response(list(bloqueios))
    except Exception as e:
        print(f"[ERRO] Falha ao buscar bloqueios: {e}")
        return Response({'erro': 'Erro ao buscar bloqueios.'}, status=500)
