from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings
from agendamentos.core.models import Agendamento, Barbeiro
from agendamentos.admin.utils import (
    is_dono,
    RestrictToOwnDataMixin,
    atribuir_barbeiro_automaticamente
)

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = '__all__'
        widgets = {
            'motivo_cancelamento': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Descreva o motivo do cancelamento'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        motivo = cleaned_data.get('motivo_cancelamento')

        if status == 'recusado' and not motivo:
            raise ValidationError({'motivo_cancelamento': "Informe o motivo do cancelamento."})
        return cleaned_data

@admin.register(Agendamento)
class AgendamentoAdmin(RestrictToOwnDataMixin, admin.ModelAdmin):
    form = AgendamentoForm
    list_display = ('nome_cliente', 'data_horario_reserva', 'status', 'barbeiro', 'disponivel')
    list_filter = ('status', 'data_horario_reserva', 'barbeiro')
    search_fields = ('nome_cliente', 'email_cliente')
    date_hierarchy = 'data_horario_reserva'
    ordering = ('-data_horario_reserva',)
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        atribuir_barbeiro_automaticamente(request, obj)

        if obj.status == 'recusado':
            self.enviar_email_cancelamento(obj)

        super().save_model(request, obj, form, change)
        obj.processar_status()

    def enviar_email_cancelamento(self, agendamento):
        if not agendamento.email_cliente:
            return

        cliente = agendamento.nome_cliente
        email = agendamento.email_cliente
        data = localtime(agendamento.data_horario_reserva).strftime('%d/%m/%Y %H:%M')
        barbeiro = agendamento.barbeiro
        motivo = agendamento.motivo_cancelamento or "O barbeiro não informou o motivo."

        link = f"{settings.DOMINIO_SITE}/barbeiro/{barbeiro.pk}/calendario"
        assunto = "❌ Seu agendamento foi cancelado"
        mensagem = (
            f"Olá {cliente},\n\nSeu agendamento no dia {data} foi cancelado.\n\n"
            f"📌 Motivo: {motivo}\n\n"
            f"Você pode remarcar acessando:\n{link}\n\n"
            f"Equipe {getattr(settings, 'NOME_NEGOCIO', 'Sua Barbearia')}"
        )

        send_mail(
            assunto,
            mensagem,
            settings.EMAIL_REMETENTE,
            [email],
            fail_silently=True
        )
