from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from .models import ConversaCliente
from clientes.models import Cliente
import unicodedata


def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto


@csrf_exempt
def whatsapp_webhook(request):
    if request.method != 'POST':
        return HttpResponse("Método não permitido", status=405)

    numero = request.POST.get('From', '').replace('whatsapp:', '')
    mensagem_recebida = request.POST.get('Body', '').strip().lower()
    resposta = MessagingResponse()

    # Verifica se já existe conversa iniciada com o número
    conversa, _ = ConversaCliente.objects.get_or_create(telefone=numero)

    # Resetar a conversa com comando 'cancelar'
    if mensagem_recebida == "cancelar":
        conversa.estado = "aguardando_inicio"
        conversa.save()
        resposta.message("❌ Conversa cancelada. Digite qualquer coisa para começar novamente.")
        return HttpResponse(str(resposta), content_type='text/xml')

    # Primeira mensagem ou reset
    if conversa.estado == "aguardando_inicio":
        resposta.message("Olá! 👋\nSeja bem-vindo à nossa barbearia ✂️\n\nEscolha uma opção para continuar:\n1️⃣ Agendar\n2️⃣ Cancelar agendamento\n3️⃣ Dúvidas")
        conversa.estado = "aguardando_menu"
        conversa.save()
        return HttpResponse(str(resposta), content_type='text/xml')

    # Etapa de escolha do menu
    if conversa.estado == "aguardando_menu":
        texto = normalizar_texto(mensagem_recebida)
        opcoes_agendar = ["1", "agendar", "agenda", "agenadr", "agnedar", "agendaar"]

        if texto in opcoes_agendar:
            cliente_existente = Cliente.objects.filter(telefone=numero).exists()
            if cliente_existente:
                resposta.message("✅ Você já está cadastrado em nosso sistema. Vamos prosseguir com o agendamento.")
                conversa.estado = "aguardando_agendamento"
            else:
                resposta.message("🔗 Para agendar, precisamos que você complete seu cadastro.\nAcesse: http://127.0.0.1:8000/cadastro")
                conversa.estado = "aguardando_inicio"
            conversa.save()
            return HttpResponse(str(resposta), content_type='text/xml')

    # Fallback caso o estado esteja indefinido
    resposta.message("⚠️ Não entendi sua mensagem. Poderia repetir?")
    return HttpResponse(str(resposta), content_type='text/xml')
