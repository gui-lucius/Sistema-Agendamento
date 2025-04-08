from django.http import JsonResponse
from django.core.mail import EmailMessage, send_mail
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
from django.utils.timezone import make_aware, is_naive, localtime
from django.views.decorators.csrf import csrf_exempt
from uuid import UUID

from .models import Agendamento, HorarioBloqueado, Barbeiro

def home(request):
    return render(request, 'index.html')

def listar_barbeiros(request):
    barbeiros = Barbeiro.objects.all()
    return render(request, 'barbeiros.html', {'barbeiros': barbeiros})

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

def notificar_barbeiro(nome_cliente, data_horario, barbeiro, servico=None):
    try:
        nome_barbearia = getattr(settings, "NOME_NEGOCIO", "Sua Barbearia")

        assunto = f"📥 Novo Agendamento Pendente - {nome_barbearia}"
        mensagem = (
            f"Olá {barbeiro.nome},\n\n"
            f"Você recebeu um novo pedido de agendamento de *{nome_cliente}* "
            f"para o dia *{data_horario.strftime('%d/%m/%Y')}* às *{data_horario.strftime('%H:%M')}*.\n"
        )

        if servico:
            mensagem += f"\n💈 Serviço solicitado: {servico}\n"

        mensagem += (
            "\nAcesse seu painel de agendamentos para aceitar ou recusar o horário.\n\n"
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
        servico = dados.get('servico')
        lembrete_minutos = dados.get('lembrete_minutos', 60)

        if not all([nome, email, data, barbeiro_id]):
            return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'erro': 'E-mail inválido.'}, status=400)

        try:
            data = parser.parse(data)
            if is_naive(data):
                data = make_aware(data)
        except Exception:
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
            barbeiro=barbeiro,
            servico=servico,
            lembrete_minutos=lembrete_minutos
        )

        notificar_barbeiro(nome, data, barbeiro, servico)

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

def api_horarios(request, barbeiro_id):
    try:
        agendamentos = Agendamento.objects.filter(
            barbeiro_id=barbeiro_id,
            status__in=['pendente', 'aceito']
        ).values('id', 'data_horario_reserva', 'status')
        return JsonResponse(list(agendamentos), safe=False)
    except Exception as e:
        print(f"[ERRO] Falha ao buscar horários (API): {e}")
        return JsonResponse({'erro': 'Erro ao buscar horários.'}, status=500)

def api_bloqueios(request, barbeiro_id):
    try:
        bloqueios = HorarioBloqueado.objects.filter(
            barbeiro_id=barbeiro_id
        ).values('id', 'data_horario', 'motivo')
        return JsonResponse(list(bloqueios), safe=False)
    except Exception as e:
        print(f"[ERRO] Falha ao buscar bloqueios (API): {e}")
        return JsonResponse({'erro': 'Erro ao buscar bloqueios.'}, status=500)

@csrf_exempt
def cancelar_agendamento(request, agendamento_id, token):
    try:
        token_uuid = UUID(str(token))
    except ValueError:
        return render(request, 'cancelamento_invalido.html')

    agendamento = Agendamento.objects.filter(id=agendamento_id, cancel_token=token_uuid).first()

    if not agendamento:
        return render(request, 'cancelamento_invalido.html')

    if request.method == 'POST':
        cliente = agendamento.nome_cliente
        horario_local = localtime(agendamento.data_horario_reserva)
        horario = horario_local.strftime('%d/%m/%Y %H:%M')

        barbeiro = agendamento.barbeiro
        barbeiro_email = barbeiro.email if barbeiro else None

        agendamento.delete()

        if barbeiro_email:
            assunto = f"❌ Agendamento cancelado - Cliente: {cliente}"
            mensagem = (
                f"Olá {barbeiro.nome},\n\n"
                f"O cliente *{cliente}* cancelou o horário agendado para {horario}.\n\n"
                "Esse horário agora está livre no sistema."
            )

            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_REMETENTE,
                [barbeiro_email],
                fail_silently=False
            )

        return render(request, 'cancelamento_confirmado.html')

    return render(request, 'confirmar_cancelamento.html', {
        'agendamento': agendamento
    })
