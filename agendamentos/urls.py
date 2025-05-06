from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)

from .views import (
    home,
    listar_barbeiros,
    calendario_com_token,
    criar_agendamento,
    horarios_ocupados,
    horarios_bloqueados,
    cancelar_agendamento,
    cliente_login_view,
    cadastro_view,
    painel_cliente,
    editar_cliente,
    editar_perfil_cliente,
    redirecionar_pos_login  # ✅ import novo
)

app_name = 'agendamentos'

urlpatterns = [
    path('', home, name='home'),

    path('barbeiros/', listar_barbeiros, name='listar_barbeiros'),
    path('calendario/<int:barbeiro_id>/', calendario_com_token, name='calendario_barbeiro'),

    path('api/agendamentos/', criar_agendamento, name='criar_agendamento'),
    path('api/horarios/<int:barbeiro_id>/', horarios_ocupados, name='horarios_ocupados'),
    path('api/bloqueios/<int:barbeiro_id>/', horarios_bloqueados, name='horarios_bloqueados'),

    path('cancelar-agendamento/<int:agendamento_id>/<uuid:token>/', cancelar_agendamento, name='cancelar_agendamento'),

    path('login/', cliente_login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='agendamentos:home'), name='logout'),
    path('cadastro/', cadastro_view, name='cadastro'),

    path('minha-conta/', painel_cliente, name='painel_cliente'),
    path('editar-perfil/', editar_cliente, name='editar_cliente'),
    path('perfil/editar/', editar_perfil_cliente, name='editar_perfil_cliente'),

    path('senha/reset/', PasswordResetView.as_view(
        template_name="auth/recuperar_senha.html"
    ), name='password_reset'),

    path('senha/reset/done/', PasswordResetDoneView.as_view(
        template_name="auth/reset_enviado.html"
    ), name='password_reset_done'),

    path('senha/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name="auth/reset_confirmar.html"
    ), name='password_reset_confirm'),

    path('senha/reset/complete/', PasswordResetCompleteView.as_view(
        template_name="auth/reset_completo.html"
    ), name='password_reset_complete'),

    path('senha/alterar/', PasswordChangeView.as_view(
        template_name="auth/alterar_senha.html"
    ), name='password_change'),

    path('senha/alterar/sucesso/', PasswordChangeDoneView.as_view(
        template_name="auth/alterar_senha_done.html"
    ), name='password_change_done'),

    # ✅ novo path para redirecionamento pós-login
    path('redirecionar/', redirecionar_pos_login, name='redirecionar'),
]
