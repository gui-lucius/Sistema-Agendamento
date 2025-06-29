from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime
from agendamentos.core.models import Agendamento, Barbeiro
from agendamentos.views.barbeiro import notificar_barbeiro, notificar_cliente
from uuid import uuid4

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 👈 ESSENCIAL
def criar_agendamento(request):
    print("=== DADOS RECEBIDOS ===")
    print(request.data)

    print("🧪 request.user =", request.user)
    print("🔐 Está autenticado?", request.user.is_authenticated)

    data = request.data
    nome = data.get('nome')
    email = data.get('email')
    servico = data.get('servico')
    lembrete_minutos = int(data.get('lembrete_minutos', 60))
    barbeiro_id = data.get('barbeiro_id')
    data_horario_str = data.get('data_horario')

    if not all([nome, email, servico, data_horario_str, barbeiro_id]):
        return Response({'erro': 'Campos obrigatórios faltando.'}, status=400)

    barbeiro = Barbeiro.objects.get(id=barbeiro_id)


    data_horario = parse_datetime(data_horario_str)

    tz = get_current_timezone()
    if data_horario and data_horario.tzinfo is None:
        data_horario = tz.localize(data_horario)

    agendamento = Agendamento.objects.create(
        barbeiro=barbeiro,
        nome_cliente=nome,
        email_cliente=email,
        servico=servico,
        lembrete_minutos=lembrete_minutos,
        data_horario_reserva=data_horario,
        cancel_token=uuid4(),
        status="aceito",
        cliente=request.user  
    )

    notificar_barbeiro(nome, data_horario, barbeiro, servico)
    notificar_cliente(agendamento)

    return Response({'mensagem': 'Agendamento criado com sucesso!'})
