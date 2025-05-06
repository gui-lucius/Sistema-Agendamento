from django.contrib import admin
from agendamentos.core.models import Barbearia

@admin.register(Barbearia)
class BarbeariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'endereco')
    search_fields = ('nome', 'telefone')
