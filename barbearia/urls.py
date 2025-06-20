from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('agendamentos.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('health/', health_check, name='health_check'),

    path(
        "google5e41cd1aba47309f.html",
        TemplateView.as_view(template_name="google5e41cd1aba47309f.html")
    ),

    path('senha/reset/', auth_views.PasswordResetView.as_view(template_name='recuperar_senha.html'), name='password_reset'),
    path('senha/reset/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='reset_enviado.html'), name='password_reset_done'),
    path('senha/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_confirmar.html'), name='password_reset_confirm'),
    path('senha/reset/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_completo.html'), name='password_reset_complete'),
    path('senha/alterar/', auth_views.PasswordChangeView.as_view(template_name='alterar_senha.html'), name='password_change'),
    path('senha/alterar/sucesso/', auth_views.PasswordChangeDoneView.as_view(template_name='alterar_sucesso.html'), name='password_change_done'),

    path('bot/', include('botwhatsapp.urls'))

]

from django.contrib.auth.models import User

def cria_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('Superusuário criado!')

cria_superuser()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
