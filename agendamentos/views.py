from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dateutil import parser
from datetime import timedelta
from django.utils.timezone import make_naive, is_aware
from .models import Agendamento, HorarioBloqueado


def home(request):
    return render(request, 'index.html')


def calendario_com_token(request):
    try:
        user = User.objects.get(username="Barbearia_RD")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        context = {
            "access_token": access_token
        }
        return render(request, "calendario.html", context)

    except User.DoesNotExist:
        return JsonResponse({"erro": "Usuário Barbearia_RD não encontrado."}, status=500)


def notificar_barbeiro(nome_cliente, data_horario):
    try:
        assunto = "Novo Agendamento Pendente"
        mensagem = (
            f"Você tem uma nova solicitação de agendamento de {nome_cliente} "
            f"para {data_horario.strftime('%d/%m/%Y %H:%M')}.\n\n"
            f"Acesse o painel administrativo para aceitar ou recusar."
        )
        send_mail(
            assunto,
            mensagem,
            settings.EMAIL_REMETENTE,
            [settings.EMAIL_DESTINO],
            fail_silently=False
        )
    except Exception as e:
        print(f"[ERRO EMAIL] Falha ao notificar barbeiro: {e}")


@api_view(['POST'])
def criar_agendamento(request):
    try:
        dados = request.data
        nome = dados.get('nome_cliente')
        email = dados.get('email_cliente')
        data = dados.get('data_horario_reserva')

        if not all([nome, email, data]):
            return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'erro': 'E-mail inválido.'}, status=400)

        try:
            data = parser.parse(data)
            if is_aware(data):
                data = make_naive(data)
        except ValueError:
            return JsonResponse({'erro': 'Data/Horário inválido.'}, status=400)

        # 🚫 VALIDA SE JÁ EXISTE AGENDAMENTO NESSE HORÁRIO
        if Agendamento.objects.filter(data_horario_reserva=data, status__in=['pendente', 'aceito']).exists():
            return JsonResponse({'erro': 'Este horário já está ocupado.'}, status=409)

        # 🚫 VALIDA SE HORÁRIO ESTÁ BLOQUEADO
        if HorarioBloqueado.objects.filter(data_horario=data).exists():
            return JsonResponse({'erro': 'Este horário está indisponível.'}, status=403)

        agendamento = Agendamento.objects.create(
            nome_cliente=nome,
            email_cliente=email,
            data_horario_reserva=data,
            status='pendente'
        )

        notificar_barbeiro(nome, data)

        return JsonResponse({'mensagem': 'Agendamento criado com sucesso!', 'id': agendamento.id}, status=201)

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao criar agendamento: {e}")
        return JsonResponse({'erro': 'Erro inesperado ao criar agendamento.'}, status=500)


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


@api_view(['GET'])
def horarios_bloqueados(request):
    try:
        bloqueios = HorarioBloqueado.objects.all().values('data_horario')
        return Response(list(bloqueios))
    except Exception as e:
        print(f"[ERRO] Falha ao buscar bloqueios: {e}")
        return Response({'erro': 'Erro ao buscar bloqueios.'}, status=500)
