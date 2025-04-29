from django.contrib import admin
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

# 🔧 Cria um form customizado para ocultar o grupo "Cliente"
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostra apenas grupos que NÃO sejam "Cliente"
        if "groups" in self.fields:
            self.fields["groups"].queryset = Group.objects.exclude(name="Cliente")

# 🔧 Remove o User padrão antes de registrar o customizado
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    form = CustomUserChangeForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Oculta usuários do grupo "Cliente" na listagem
        return qs.exclude(groups__name='Cliente')

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name", "email")}),
        ("Permissões", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
            )
        }),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2"),
        }),
    )

    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
