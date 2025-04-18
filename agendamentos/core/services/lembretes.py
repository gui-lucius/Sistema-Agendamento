from django.utils.timezone import now, localtime
from django.core.mail import EmailMessage
from datetime import timedelta
from django.conf import settings
from agendamentos.core.models import Agendamento

def enviar_lembretes_agendamentos():
    agora = now()
    daqui_uma_hora = agora + timedelta(hours=1)

    agendamentos = Agendamento.objects.filter(
        data_horario_reserva__gte=agora,
        data_horario_reserva__lte=daqui_uma_hora,
        status='aceito',
        lembrete_enviado=False
    )

    total_enviados = 0

    for agendamento in agendamentos:
        try:
            horario_local = localtime(agendamento.data_horario_reserva)
            horario_formatado = horario_local.strftime('%d/%m/%Y às %H:%M')

            barbeiro = agendamento.barbeiro.nome if agendamento.barbeiro else "nosso barbeiro"
            servico = getattr(agendamento, 'servico', 'Serviço não especificado')

            dominio = getattr(settings, 'DOMINIO_SITE', 'http://127.0.0.1:8000')
            link_cancelamento = f"{dominio}/cancelar-agendamento/{agendamento.pk}/{agendamento.cancel_token}/"

            nome_negocio = getattr(settings, "NOME_NEGOCIO", "Barbearia")

            assunto = f"⏰ Lembrete do seu horário na {nome_negocio}!"
            mensagem = (
                f"Olá {agendamento.nome_cliente},\n\n"
                f"Este é um lembrete do seu agendamento com {barbeiro} na {nome_negocio}.\n\n"
                f"📅 Data e Hora: {horario_formatado}\n"
                f"💈 Serviço: {servico}\n\n"
                f"Se precisar cancelar, use o link abaixo:\n{link_cancelamento}\n\n"
                f"Nos vemos em breve! 😎\n"
                f"Equipe {nome_negocio}"
            )

            email = EmailMessage(
                subject=assunto,
                body=mensagem,
                to=[agendamento.email_cliente]
            )
            email.send(fail_silently=False)

            agendamento.lembrete_enviado = True
            agendamento.save(update_fields=['lembrete_enviado'])

            total_enviados += 1

        except Exception as e:
            print(f"[ERRO] Falha ao enviar lembrete para {agendamento.email_cliente}: {e}")

    return total_enviados
