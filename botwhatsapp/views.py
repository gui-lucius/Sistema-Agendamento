from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from .models import ConversaCliente
from clientes.models import Cliente
from datetime import timezone
from agendamentos.core.models import Barbeiro
from agendamentos.core.models import Agendamento
from agendamentos.core.models import HorarioBloqueado, BloqueioSemanalPadrao
import unicodedata
from django.utils.timezone import make_aware
from datetime import datetime, timedelta, time
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

def formatar_horario(horario):
    partes = ''.join(filter(str.isdigit, horario))
    if len(partes) == 4:
        return f"{partes[:2]}:{partes[2:]}"
    elif len(partes) == 2:
        return f"{partes}:00"
    elif len(partes) == 3:
        return f"{partes[0]}:{partes[1:]}"
    return horario

def horarios_disponiveis(barbeiro, data_obj):
    hora_inicio = 9
    hora_fim = 21
    intervalo = 1  # 1 hora
    horarios = []

    for h in range(hora_inicio, hora_fim):
        data_hora = make_aware(datetime.combine(data_obj, time(h, 0)))

        existe_agendamento = Agendamento.objects.filter(
            barbeiro=barbeiro,
            data_horario_reserva=data_hora,
            status__in=['pendente', 'aceito']
        ).exists()

        bloqueado = HorarioBloqueado.objects.filter(
            barbeiro=barbeiro,
            data_horario=data_hora
        ).exists()

        bloqueio_padrao = BloqueioSemanalPadrao.objects.filter(
            barbeiro=barbeiro,
            dia_semana=data_obj.weekday(),
            hora_inicio=time(h, 0)  # ⬅️ corrigido aqui
        ).exists()

        if not existe_agendamento and not bloqueado and not bloqueio_padrao:
            horarios.append(data_hora.strftime('%H:%M'))

    return horarios

@csrf_exempt
def whatsapp_webhook(request):
    if request.method != 'POST':
        return HttpResponse("Método não permitido", status=405)

    numero = request.POST.get('From', '').replace('whatsapp:', '')
    numero = numero.replace('+55', '')
    mensagem_recebida = request.POST.get('Body', '').strip().lower()
    resposta = MessagingResponse()

    conversa, _ = ConversaCliente.objects.get_or_create(telefone=numero)

    if normalizar_texto(mensagem_recebida) in ["resetar", "voltar", "início", "inicio", "começar", "menu"]:
        conversa.estado = "aguardando_inicio"
        conversa.save()
        resposta.message("🔄 Fluxo reiniciado! Digite qualquer coisa para começar novamente.")
        return HttpResponse(str(resposta), content_type='text/xml')

    if conversa.estado == "aguardando_inicio":
        resposta.message("Olá! 👋\nSeja bem-vindo à nossa barbearia ✂️\n\nEscolha uma opção para continuar:\n1️⃣ Agendar\n2️⃣ Cancelar agendamento\n3️⃣ Dúvidas")
        conversa.estado = "aguardando_menu"
        conversa.save()
        return HttpResponse(str(resposta), content_type='text/xml')

    if conversa.estado == "aguardando_menu":
        texto = normalizar_texto(mensagem_recebida)
        opcoes_agendar = ["1", "agendar", "agenda", "agenadr", "agnedar", "agendaar"]
        opcoes_cancelar = ["2", "cancelar", "cancelar agendamento", "deletar"]
        opcoes_duvidas = ["3", "duvidas", "dúvidas", "perguntas", "ajuda"]

        if texto in opcoes_agendar:
            cliente_existente = Cliente.objects.filter(telefone=numero).exists()

            if not cliente_existente and len(numero) == 10:
                numero_com_nove = numero[:2] + '9' + numero[2:]
                cliente_existente = Cliente.objects.filter(telefone=numero_com_nove).exists()

            if cliente_existente:
                barbeiros = Barbeiro.objects.all()
                texto_barbeiros = "\n".join([f"• {b.nome}" for b in barbeiros])
                resposta.message(f"✅ Você já está cadastrado em nosso sistema. Vamos prosseguir com o agendamento.\n\nEscolha um dos barbeiros disponíveis:\n{texto_barbeiros}")
                conversa.estado = "aguardando_barbeiro"
            else:
                resposta.message("🔗 Para agendar, precisamos que você complete seu cadastro.\nAcesse: http://127.0.0.1:8000/cadastro")
                conversa.estado = "aguardando_inicio"
            conversa.save()
            return HttpResponse(str(resposta), content_type='text/xml')
        
        elif texto in opcoes_cancelar:
            try:
                cliente = Cliente.objects.get(telefone=numero)
            except Cliente.DoesNotExist:
                numero_com_nove = numero[:2] + '9' + numero[2:]
                try:
                    cliente = Cliente.objects.get(telefone=numero_com_nove)
                except Cliente.DoesNotExist:
                    resposta.message("❌ Você ainda não possui cadastro em nosso sistema.")
                    return HttpResponse(str(resposta), content_type='text/xml')

            agora = make_aware(datetime.now())
            agendamentos = Agendamento.objects.filter(
                nome_cliente=cliente.nome,
                email_cliente=cliente.email,
                data_horario_reserva__gte=agora,
                status="aceito"
            ).order_by('data_horario_reserva')

            if not agendamentos.exists():
                resposta.message("📭 Você não possui nenhum agendamento futuro para cancelar.")
                return HttpResponse(str(resposta), content_type='text/xml')

            texto_agendamentos = "🗓️ Seus agendamentos futuros:\n\n"
            for ag in agendamentos:
                texto_agendamentos += f"• {ag.data_horario_reserva.strftime('%d/%m %H:%M')}\n"
                print("[DEBUG] Agendamento salvo:", ag.data_horario_reserva.isoformat())  # 👈 INSIRA AQUI
            texto_agendamentos += "\nDigite o dia e hora exatos que deseja cancelar (ex: 24/05 15:00)"
            conversa.estado = "aguardando_cancelamento"
            conversa.save()
            resposta.message(texto_agendamentos)
            return HttpResponse(str(resposta), content_type='text/xml')
        
        elif texto in opcoes_duvidas:
            resposta.message("📌 Algumas dúvidas comuns:\n\n• Qual o horário de funcionamento?\nDas 9h às 20h.\n• Posso agendar para hoje?\nSim, se houver horários disponíveis.\n\nDigite qualquer coisa para voltar ao menu.")
            conversa.estado = "aguardando_inicio"
            conversa.save()
            return HttpResponse(str(resposta), content_type='text/xml')

        else:
            resposta.message("⚠️ Opção inválida. Por favor, responda com:\n1️⃣ Agendar\n2️⃣ Cancelar agendamento\n3️⃣ Dúvidas")
            return HttpResponse(str(resposta), content_type='text/xml')


    if conversa.estado == "aguardando_barbeiro":
        mensagem_normalizada = normalizar_texto(mensagem_recebida)
        barbeiros = Barbeiro.objects.all()
        barbeiro_encontrado = None

        for barbeiro in barbeiros:
            nome_normalizado = normalizar_texto(barbeiro.nome)
            if nome_normalizado in mensagem_normalizada or mensagem_normalizada in nome_normalizado:
                barbeiro_encontrado = barbeiro
                break

        if barbeiro_encontrado:
            conversa.barbeiro = barbeiro_encontrado
            conversa.estado = "aguardando_data"
            conversa.save()
            resposta.message(f"✅ Barbeiro selecionado: {barbeiro_encontrado.nome}\nDigite o dia que deseja agendar (Escreva no formato dia/mes)")
        else:
            texto = "❌ Barbeiro não encontrado. Escolha um dos seguintes:\n"
            for b in barbeiros:
                texto += f"• {b.nome}\n"
            resposta.message(texto)

        return HttpResponse(str(resposta), content_type='text/xml')

    if conversa.estado == "aguardando_data":
        try:
            data_formatada = datetime.strptime(mensagem_recebida, "%d/%m")
            data_formatada = data_formatada.replace(year=datetime.now().year)
            dia_semana = data_formatada.strftime('%A').capitalize()
            conversa.estado = f"confirmando_data|{data_formatada.strftime('%Y-%m-%d')}"
            conversa.save()
            resposta.message(f"📅 Dia {data_formatada.strftime('%d/%m')}, {dia_semana}, está correto?")
        except ValueError:
            resposta.message("⚠️ Formato inválido. Digite no formato dia/mes, como 08/05.")

        return HttpResponse(str(resposta), content_type='text/xml')

    if conversa.estado.startswith("confirmando_data"):
        texto = normalizar_texto(mensagem_recebida)
        if texto in ["sim", "correto", "sim sim", "isso"]:
            data_str = conversa.estado.split("|")[1]
            data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
            horarios = horarios_disponiveis(conversa.barbeiro, data_obj)
            if horarios:
                texto_horarios = "\n".join([f"• {h}" for h in horarios])
                resposta.message(f"⏰ Horários disponíveis em {data_obj.strftime('%d/%m')}\n{texto_horarios}\n\nDigite o horário desejado:")
                conversa.estado = f"aguardando_horario|{data_str}"
            else:
                resposta.message("❌ Nenhum horário disponível nesse dia. Tente outro dia.")
                conversa.estado = "aguardando_data"
        elif texto in ["nao", "não", "n", "cancelar", "errado"]:
            resposta.message("Digite o dia que deseja agendar (Escreva no formato dia/mes)")
            conversa.estado = "aguardando_data"
        else:
            resposta.message("⚠️ Não entendi. Por favor, responda com 'sim' ou 'não'.")
        conversa.save()
        return HttpResponse(str(resposta), content_type='text/xml')

    if conversa.estado.startswith("aguardando_horario"):
        horario_str = formatar_horario(mensagem_recebida)
        data_str = conversa.estado.split("|")[1]

        try:
            # Tenta buscar o cliente com e sem o nono dígito
            try:
                cliente = Cliente.objects.get(telefone=numero)
            except Cliente.DoesNotExist:
                numero_com_nove = numero[:2] + '9' + numero[2:]
                cliente = Cliente.objects.get(telefone=numero_com_nove)

            # Cria datetime completo com timezone
            data_completa = datetime.strptime(f"{data_str} {horario_str}", "%Y-%m-%d %H:%M")
            data_completa = data_completa.replace(tzinfo=timezone.utc)

            # Armazena data/hora e solicita o serviço
            conversa.estado = f"aguardando_servico|{data_str}|{horario_str}"
            conversa.save()
            resposta.message(
                "🧾 Agora escolha o serviço desejado:\n\n"
                "• Corte - R$35\n"
                "• Corte + Barba - R$60\n"
                "• Descoloração - R$150\n"
                "• Pigmentação - R$60\n"
                "• Plano Mensal - R$100\n\n"
                "Digite exatamente como aparece acima ou algo próximo (ex: 'corte', 'barba')."
            ) 
            return HttpResponse(str(resposta), content_type='text/xml') 

        except Exception as e:
            print("[ERRO AO AGENDAR]", e)
            resposta.message("❌ Erro ao confirmar o agendamento. Tente novamente.")
            conversa.estado = "aguardando_inicio"
            conversa.save()
            return HttpResponse(str(resposta), content_type='text/xml')
            

    if conversa.estado.startswith("aguardando_servico"):
        data_str, hora_str = conversa.estado.split("|")[1:]
        servico_escolhido = mensagem_recebida.strip()

        opcoes_servico = {
            "corte": "Corte - R$35",
            "corte + barba": "Corte + Barba - R$60",
            "descoloracao": "Descoloração - R$150",
            "pigmentacao": "Pigmentação - R$60",
            "plano mensal": "Plano Mensal - R$100"
        }

        texto_normalizado = normalizar_texto(servico_escolhido)
        servico_formatado = None

        for chave, valor in opcoes_servico.items():
            if chave in texto_normalizado:
                servico_formatado = valor
                break

        if not servico_formatado:
            resposta.message("⚠️ Serviço não reconhecido. Escolha uma das opções abaixo:\n\n" +
                "\n".join([f"• {v}" for v in opcoes_servico.values()]))
            return HttpResponse(str(resposta), content_type='text/xml')

        try:
            # Buscar cliente (com ou sem o nono dígito)
            try:
                cliente = Cliente.objects.get(telefone=numero)
            except Cliente.DoesNotExist:
                numero_com_nove = numero[:2] + '9' + numero[2:]
                cliente = Cliente.objects.get(telefone=numero_com_nove)

            # Buscar usuário (User) vinculado ao e-mail do cliente
            from django.contrib.auth.models import User
            try:
                usuario = User.objects.get(email=cliente.email)
            except User.DoesNotExist:
                usuario = None  # Continua mesmo sem o User

            # Cria datetime completo com timezone
            data_completa = make_aware(datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M"))

            # Cria agendamento com todos os campos
            Agendamento.objects.create(
                user=usuario,
                nome_cliente=cliente.nome,
                email_cliente=cliente.email,
                barbeiro=conversa.barbeiro,
                data_horario_reserva=data_completa,
                servico=servico_formatado,
                status="aceito"
            )

            resposta.message(
                f"✅ Agendamento confirmado para {data_completa.strftime('%d/%m às %H:%M')} com {conversa.barbeiro.nome}.\n💈 Serviço: {servico_formatado}"
            )
            conversa.estado = "aguardando_inicio"
            conversa.save()

        except Exception as e:
            print("[ERRO AO AGENDAR]", e)
            resposta.message("❌ Erro ao confirmar o agendamento. Tente novamente.")
            conversa.estado = "aguardando_inicio"
            conversa.save()

        return HttpResponse(str(resposta), content_type='text/xml')
    
    if conversa.estado == "aguardando_cancelamento":
        try:
            data_bruta = datetime.strptime(mensagem_recebida, "%d/%m %H:%M")
            data_ajustada = data_bruta.replace(year=datetime.now().year)
            data_cancelamento = data_ajustada.replace(tzinfo=timezone.utc)

            try:
                cliente = Cliente.objects.get(telefone=numero)
            except Cliente.DoesNotExist:
                numero_com_nove = numero[:2] + '9' + numero[2:]
                cliente = Cliente.objects.get(telefone=numero_com_nove)

            # 🔍 DEBUG PRINTS
            print("[DEBUG] Cliente:", cliente.nome, cliente.email)
            print("[DEBUG] Data solicitada para cancelamento:", data_cancelamento)

            from datetime import timedelta
            inicio = data_cancelamento.replace(second=0, microsecond=0)
            fim = inicio + timedelta(minutes=1)

            print("[DEBUG] Intervalo de busca:", inicio, "até", fim)

            agendamento = Agendamento.objects.filter(
                nome_cliente=cliente.nome,
                email_cliente=cliente.email,
                data_horario_reserva__range=(inicio, fim),
                status="aceito"
            ).first()

            if not agendamento:
                print("[DEBUG] Nenhum agendamento encontrado nesse intervalo.")
                resposta.message("❌ Nenhum agendamento encontrado com essa data e hora.")
            else:
                print("[DEBUG] Agendamento encontrado:", agendamento)
                agendamento.delete()
                resposta.message(
                    f"✅ Agendamento para {data_cancelamento.strftime('%d/%m %H:%M')} foi cancelado com sucesso."
                )

            conversa.estado = "aguardando_inicio"
            conversa.save()
            return HttpResponse(str(resposta), content_type='text/xml')

        except ValueError:
            resposta.message("⚠️ Formato inválido. Por favor, digite como no exemplo: 24/05 15:00")
            return HttpResponse(str(resposta), content_type='text/xml')

    resposta.message("⚠️ Não entendi sua mensagem. Poderia repetir?")
    return HttpResponse(str(resposta), content_type='text/xml')
