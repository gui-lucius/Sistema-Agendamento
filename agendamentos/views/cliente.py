from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from clientes.decorators import cliente_required
from agendamentos.forms.cliente import ClienteForm
from clientes.models import Cliente
from agendamentos.core.models import Agendamento
from datetime import date, timedelta
from django.utils.timezone import now
from django.db.models import Q

def cliente_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("agendamentos:redirecionar")  # ✅ usa o roteador de grupo
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "agendamentos/login.html")

def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        senha = request.POST.get("senha")

        print("📥 Dados recebidos:", nome, email, telefone)

        if not all([nome, email, senha, telefone]):
            print("⚠️ Campos obrigatórios ausentes.")
            return render(request, "agendamentos/cadastro.html", {
                "erro": "Todos os campos são obrigatórios."
            })

        if User.objects.filter(username=email).exists():
            print("❌ E-mail já cadastrado:", email)
            return render(request, "agendamentos/cadastro.html", {
                "erro": "Este e-mail já está em uso."
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )
        print("✅ Usuário criado com ID:", user.id)

        cliente = Cliente.objects.create(
            user=user,
            nome=nome,
            telefone=telefone,
            email=email
        )
        print("✅ Cliente criado com ID:", cliente.id)

        grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
        user.groups.add(grupo_cliente)
        print("👥 Adicionado ao grupo 'Cliente'")

        return redirect("agendamentos:login")

    return render(request, "agendamentos/cadastro.html")

@cliente_required
def painel_cliente(request):
    cliente, _ = Cliente.objects.get_or_create(
        user=request.user,
        defaults={'nome': request.user.first_name}
    )

    hoje = date.today()
    inicio_semana = hoje
    fim_semana = hoje + timedelta(days=6)

    # ✅ Aqui é a correção principal: request.user no lugar de request.user.cliente
    agendamentos = Agendamento.objects.filter(
        cliente=request.user,
        data_horario_reserva__date__range=(inicio_semana, fim_semana)
    ).order_by('data_horario_reserva')

    agendamentos_passados = Agendamento.objects.filter(
        cliente=request.user,
        data_horario_reserva__date__lt=hoje
    ).order_by('-data_horario_reserva')

    return render(request, 'agendamentos/painel_cliente.html', {
        'user': request.user,
        'cliente': cliente,
        'agendamentos': agendamentos,
        'agendamentos_passados': agendamentos_passados
    })

@cliente_required
def editar_cliente(request):
    user = request.user
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")

        if not nome or not email:
            messages.error(request, "Nome e e-mail são obrigatórios.")
            return redirect('agendamentos:editar_cliente')

        user.first_name = nome
        user.email = email
        user.username = email
        user.save()

        messages.success(request, "Dados atualizados com sucesso.")
        return redirect('agendamentos:painel_cliente')

    return render(request, 'agendamentos/editar_cliente.html', {'user': user})

import os
from django.conf import settings

@cliente_required
def editar_perfil_cliente(request):
    cliente, _ = Cliente.objects.get_or_create(
        user=request.user,
        defaults={'nome': request.user.first_name}
    )

    if request.method == 'POST':
        # 🔥 Lógica de exclusão da foto
        if 'excluir_foto' in request.POST:
            if cliente.foto:
                # Remove o arquivo da pasta, se existir
                caminho = cliente.foto.path
                if os.path.exists(caminho):
                    os.remove(caminho)

                # Limpa o campo no banco
                cliente.foto.delete(save=False)
                cliente.foto = None
                cliente.save()

                messages.success(request, "Foto excluída com sucesso.")
            else:
                messages.warning(request, "Nenhuma foto para excluir.")
            return redirect('agendamentos:editar_perfil_cliente')

        # 🔄 Atualização normal do formulário
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect('agendamentos:painel_cliente')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'agendamentos/editar_perfil.html', {
        'form': form,
        'cliente': cliente
    })
