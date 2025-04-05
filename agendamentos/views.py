from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dateutil import parser
from datetime import timedelta
from django.utils.timezone import make_naive, is_aware
from .models import Agendamento, HorarioBloqueado, Barbeiro


def home(request):
    return render(request, 'index.html')


# NOVA VIEW: Lista todos os barbeiros
def listar_barbeiros(request):
    barbeiros = Barbeiro.objects.all()
    return render(request, 'barbeiros.html', {'barbeiros': barbeiros})


# MODIFICADA: Agora aceita o ID do barbeiro e mostra o calendário só dele
def calendario_com_token(request, barbeiro_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
    try:
        user = barbeiro.usuario
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        context = {
            "access_token": access_token,
            "barbeiro": barbeiro
        }
        return render(request, "calendario.html", context)
    except Exception as e:
        return JsonResponse({"erro": f"Erro ao gerar token: {str(e)}"}, status=500)


# ✅ ATUALIZADA: envia para o e-mail do barbeiro específico
def notificar_barbeiro(nome_cliente, data_horario, barbeiro):
    try:
        nome_barbearia = getattr(settings, "NOME_NEGOCIO", "Sua Barbearia")

        assunto = f"📥 Novo Agendamento Pendente - {nome_barbearia}"
        mensagem = (
            f"Olá {barbeiro.nome},\n\n"
            f"Você recebeu um novo pedido de agendamento de *{nome_cliente}* "
            f"para o dia *{data_horario.strftime('%d/%m/%Y')}* às *{data_horario.strftime('%H:%M')}*.\n\n"
            "Acesse seu painel de agendamentos para aceitar ou recusar o horário.\n\n"
            f"Atenciosamente,\n{nome_barbearia}"
        )

        email = EmailMessage(
            subject=assunto,
            body=mensagem,
            from_email=f'{nome_barbearia} <{settings.EMAIL_REMETENTE}>',
            to=[barbeiro.email],
        )
        email.send(fail_silently=False)
    except Exception as e:
        print(f"[ERRO EMAIL] Falha ao notificar barbeiro: {e}")



@api_view(['POST'])
def criar_agendamento(request):
    try:
        dados = request.data
        nome = dados.get('nome_cliente')
        email = dados.get('email_cliente')
        data = dados.get('data_horario_reserva')
        barbeiro_id = dados.get('barbeiro_id')

        if not all([nome, email, data, barbeiro_id]):
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

        barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)

        if Agendamento.objects.filter(
            data_horario_reserva=data,
            barbeiro=barbeiro,
            status__in=['pendente', 'aceito']
        ).exists():
            return JsonResponse({'erro': 'Este horário já está ocupado.'}, status=409)

        if HorarioBloqueado.objects.filter(
            barbeiro=barbeiro,
            data_horario=data
        ).exists():
            return JsonResponse({'erro': 'Este horário está indisponível.'}, status=403)

        agendamento = Agendamento.objects.create(
            nome_cliente=nome,
            email_cliente=email,
            data_horario_reserva=data,
            status='pendente',
            barbeiro=barbeiro
        )

        # ✅ Agora com o e-mail do barbeiro correto
        notificar_barbeiro(nome, data, barbeiro)

        return JsonResponse({'mensagem': 'Agendamento criado com sucesso!', 'id': agendamento.id}, status=201)

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao criar agendamento: {e}")
        return JsonResponse({'erro': 'Erro inesperado ao criar agendamento.'}, status=500)


@api_view(['GET'])
def horarios_ocupados(request, barbeiro_id):
    try:
        barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
        horarios = Agendamento.objects.filter(
            barbeiro=barbeiro,
            status__in=['pendente', 'aceito']
        ).values('data_horario_reserva', 'status')
        return Response(list(horarios))
    except Exception as e:
        print(f"[ERRO] Falha ao buscar horários ocupados: {e}")
        return Response({'erro': 'Erro ao buscar horários ocupados.'}, status=500)


@api_view(['GET'])
def horarios_bloqueados(request, barbeiro_id):
    try:
        barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
        bloqueios = HorarioBloqueado.objects.filter(barbeiro=barbeiro).values('data_horario')
        return Response(list(bloqueios))
    except Exception as e:
        print(f"[ERRO] Falha ao buscar bloqueios: {e}")
        return Response({'erro': 'Erro ao buscar bloqueios.'}, status=500)
