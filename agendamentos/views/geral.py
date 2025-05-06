from datetime import datetime, timedelta
from uuid import UUID
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect  # <-- Aqui está o fix
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from clientes.models import Cliente  # <-- Model Cliente

from agendamentos.core.models import (
    Barbeiro,
    HorarioBloqueado,
    BloqueioSemanalPadrao,
    Agendamento,
)

def home(request):
    return render(request, 'agendamentos/index.html')

@login_required(login_url='agendamentos:login')
def listar_barbeiros(request):
    barbeiros = Barbeiro.objects.all()
    return render(request, 'agendamentos/barbeiros.html', {'barbeiros': barbeiros})

@login_required(login_url='agendamentos:login')
def calendario_com_token(request, barbeiro_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)

    try:
        cliente = Cliente.objects.get(user=request.user)
        refresh = RefreshToken.for_user(barbeiro.usuario)
        access_token = str(refresh.access_token)

        context = {
            "access_token": access_token,
            "barbeiro": barbeiro,
            "cliente": {
                "nome": cliente.nome,
                "email": cliente.email,
                "telefone": cliente.telefone
            }
        }
        return render(request, "agendamentos/calendario.html", context)

    except Cliente.DoesNotExist:
        print("[ERRO] Cliente não encontrado para o usuário logado.")
        return redirect("agendamentos:editar_perfil_cliente")

    except Exception as e:
        print(f"[ERRO GERAL] {e}")
        return JsonResponse({"erro": f"Erro ao gerar token ou buscar cliente: {str(e)}"}, status=500)

@api_view(['GET'])
def horarios_ocupados(request, barbeiro_id):
    try:
        barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
        agendamentos = Agendamento.objects.filter(
            barbeiro=barbeiro,
            status__in=['pendente', 'aceito']
        )

        eventos = [{
            "data_horario_reserva": ag.data_horario_reserva.isoformat(),
            "status": ag.status
        } for ag in agendamentos]

        return Response(eventos)

    except Exception as e:
        print(f"[ERRO] Falha ao buscar horários ocupados: {e}")
        return Response({'erro': 'Erro ao buscar horários ocupados.'}, status=500)

@api_view(['GET'])
def horarios_bloqueados(request, barbeiro_id):
    try:
        barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
        bloqueios = list(HorarioBloqueado.objects.filter(barbeiro=barbeiro).values('data_horario'))
        hoje = datetime.today()
        dias_a_gerar = 365
        horarios_semanais = BloqueioSemanalPadrao.objects.filter(barbeiro=barbeiro)

        for i in range(dias_a_gerar):
            data = hoje + timedelta(days=i)
            dia_semana = data.weekday()

            for b in horarios_semanais.filter(dia_semana=dia_semana):
                hora_atual = datetime.combine(data.date(), b.hora_inicio)
                hora_final = datetime.combine(data.date(), b.hora_fim)

                while hora_atual <= hora_final:
                    bloqueios.append({'data_horario': hora_atual})
                    hora_atual += timedelta(hours=1)

        return Response(bloqueios)

    except Exception as e:
        print(f"[ERRO] Falha ao buscar bloqueios: {e}")
        return Response({'erro': 'Erro ao buscar bloqueios.'}, status=500)

@csrf_exempt
def cancelar_agendamento(request, agendamento_id, token):
    token_uuid = UUID(str(token))
    agendamento = Agendamento.objects.filter(id=agendamento_id, cancel_token=token_uuid).first()

    if not agendamento:
        return render(request, 'cancelamentos/cancelamento_invalido.html')

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

        return render(request, 'cancelamentos/cancelamento_confirmado.html')

    return render(request, 'cancelamentos/confirmar_cancelamento.html', {'agendamento': agendamento})
