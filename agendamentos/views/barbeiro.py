from django.http import JsonResponse
from django.core.mail import EmailMessage, send_mail
from django.conf import settings

# 🔔 Notifica o barbeiro com os dados do cliente
def notificar_barbeiro(nome_cliente, data_horario, barbeiro, servico=None):
    try:
        nome_barbearia = getattr(settings, "NOME_NEGOCIO", "Sua Barbearia")
        assunto = f"📌 Novo Agendamento Confirmado - {nome_barbearia}"
        mensagem = (
            f"Olá {barbeiro.nome},\n\n"
            f"*{nome_cliente}* agendou para {data_horario.strftime('%d/%m/%Y %H:%M')}."
        )

        if servico:
            mensagem += f"\n💈 Serviço: {servico}\n"

        mensagem += f"\nEquipe {nome_barbearia}"

        email = EmailMessage(
            subject=assunto,
            body=mensagem,
            from_email=f'{nome_barbearia} <{settings.EMAIL_REMETENTE}>',
            to=[barbeiro.email],
        )
        email.send(fail_silently=False)
    except Exception as e:
        print(f"[ERRO EMAIL] Falha ao notificar barbeiro: {e}")


# ✅ Nova função: Notifica o cliente com link de cancelamento
def notificar_cliente(agendamento):
    try:
        assunto = "✅ Confirmação de Agendamento"
        corpo = f"""
Olá {agendamento.nome_cliente},

Seu agendamento para o serviço: {agendamento.servico}
com o barbeiro {agendamento.barbeiro.nome}
foi confirmado para o dia {agendamento.data_horario_reserva.strftime('%d/%m/%Y às %H:%M')}.

Caso queira cancelar, clique no link abaixo:
{settings.DOMINIO_SITE}/cancelar-agendamento/{agendamento.id}/{agendamento.cancel_token}/

Até logo! 👋
Equipe {getattr(settings, "NOME_NEGOCIO", "Sua Barbearia")}
"""

        send_mail(
            assunto,
            corpo,
            settings.EMAIL_REMETENTE,
            [agendamento.email_cliente],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[ERRO EMAIL] Falha ao notificar cliente: {e}")
