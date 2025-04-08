from django.contrib import admin
from django import forms
from django.forms.widgets import DateInput  
from django.contrib.auth.models import Group
from .models import Agendamento, HorarioBloqueado, Barbeiro
from datetime import datetime, timedelta

class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = '__all__'
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'user',
            })
        }

class HorarioBloqueadoForm(forms.ModelForm):
    data = forms.DateField(
        label="Data",
        required=True,
        widget=DateInput(attrs={'type': 'date'})  
    )
    bloquear_dia_todo = forms.BooleanField(required=False, label="Bloquear o dia todo")
    hora_inicial = forms.TimeField(required=False, label='Hora Inicial')
    hora_final = forms.TimeField(required=False, label='Hora Final')

    class Meta:
        model = HorarioBloqueado
        fields = ['barbeiro', 'motivo']  

    def clean(self):
        cleaned_data = super().clean()
        bloquear_dia_todo = cleaned_data.get('bloquear_dia_todo')
        hora_inicial = cleaned_data.get('hora_inicial')
        hora_final = cleaned_data.get('hora_final')

        if not bloquear_dia_todo:
            if not hora_inicial or not hora_final:
                raise forms.ValidationError("Informe hora inicial e final ou marque 'Bloquear o dia todo'.")
            if hora_inicial > hora_final:
                raise forms.ValidationError("A hora final deve ser maior ou igual à inicial.")
        return cleaned_data

@admin.register(HorarioBloqueado)
class HorarioBloqueadoAdmin(admin.ModelAdmin):
    form = HorarioBloqueadoForm
    list_display = ('data_horario', 'motivo', 'barbeiro')
    search_fields = ('data_horario', 'motivo', 'barbeiro__nome')
    list_filter = ('barbeiro',)
    ordering = ('-data_horario',)
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        barbeiro = form.cleaned_data['barbeiro']
        data = form.cleaned_data['data']
        motivo = form.cleaned_data['motivo']
        bloquear_dia_todo = form.cleaned_data.get('bloquear_dia_todo')

        if bloquear_dia_todo:
            hora_inicial = datetime.strptime("09:00", "%H:%M").time()
            hora_final = datetime.strptime("21:00", "%H:%M").time()
        else:
            hora_inicial = form.cleaned_data['hora_inicial']
            hora_final = form.cleaned_data['hora_final']

        atual = datetime.combine(data, hora_inicial)
        fim = datetime.combine(data, hora_final)

        while atual <= fim:
            HorarioBloqueado.objects.get_or_create(
                barbeiro=barbeiro,
                data_horario=atual,
                defaults={'motivo': motivo}
            )
            atual += timedelta(hours=1)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        if obj and obj.barbeiro.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "barbeiro" and not (request.user.is_superuser or is_dono(request.user)):
            try:
                barbeiro = Barbeiro.objects.get(usuario=request.user)
                kwargs["queryset"] = Barbeiro.objects.filter(pk=barbeiro.pk)
                kwargs["initial"] = barbeiro
            except Barbeiro.DoesNotExist:
                kwargs["queryset"] = Barbeiro.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Verifica se é do grupo Dono
def is_dono(user):
    return user.groups.filter(name='Dono').exists()

# Agendamentos
@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'data_horario_reserva', 'status', 'barbeiro', 'disponivel')
    list_display_links = ('nome_cliente', 'data_horario_reserva')
    list_filter = ('status', 'data_horario_reserva', 'barbeiro')
    search_fields = ('nome_cliente', 'email_cliente')
    date_hierarchy = 'data_horario_reserva'
    ordering = ('-data_horario_reserva',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs
        return qs.filter(barbeiro__usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        if obj and obj.barbeiro.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not (request.user.is_superuser or is_dono(request.user)) and not obj.barbeiro_id:
            try:
                obj.barbeiro = Barbeiro.objects.get(usuario=request.user)
            except Barbeiro.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
        obj.processar_status()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "barbeiro" and not (request.user.is_superuser or is_dono(request.user)):
            try:
                barbeiro = Barbeiro.objects.get(usuario=request.user)
                kwargs["queryset"] = Barbeiro.objects.filter(pk=barbeiro.pk)
                kwargs["initial"] = barbeiro
            except Barbeiro.DoesNotExist:
                kwargs["queryset"] = Barbeiro.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Barbeiros
@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    form = BarbeiroForm
    list_display = ('nome', 'email', 'usuario')
    search_fields = ('nome', 'email')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_dono(request.user):
            return qs
        return qs.filter(usuario=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_dono(request.user):
            return True
        if obj and obj.usuario != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
