from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from clientes.decorators import cliente_required


def cliente_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and user.groups.filter(name="Cliente").exists():
            login(request, user)
            return redirect("agendamentos:home")
        messages.error(request, "Usuário ou senha inválidos ou não autorizado.")

    return render(request, "agendamentos/login.html")


def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if not all([nome, email, senha]):
            return render(request, "agendamentos/cadastro.html", {
                "erro": "Todos os campos são obrigatórios."
            })
        if User.objects.filter(username=email).exists():
            return render(request, "agendamentos/cadastro.html", {
                "erro": "Este e-mail já está em uso."
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )
        grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')
        user.groups.add(grupo_cliente)

        return redirect("agendamentos:login")

    return render(request, "agendamentos/cadastro.html")


@cliente_required
def painel_cliente(request):
    return render(request, 'agendamentos/painel_cliente.html', {'user': request.user})


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
