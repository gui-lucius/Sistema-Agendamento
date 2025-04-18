from pathlib import Path
import os
from datetime import timedelta
import dj_database_url

# Caminho base do projeto (nível de manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Segurança e Debug
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'chave-de-desenvolvimento')
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Aplicativos instalados
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agendamentos',
    'clientes',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'clientes.middleware.ClienteSessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs
ROOT_URLCONF = 'barbearia.urls'

# Templates (caminho direto para a pasta templates no mesmo nível do manage.py)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



# WSGI
WSGI_APPLICATION = 'barbearia.wsgi.application'

# Banco de dados (prioridade para DATABASE_URL, senão usa sqlite)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Autenticação personalizada
AUTHENTICATION_BACKENDS = [
    'clientes.backends.ClienteBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# E-mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sistemadeagenda5@gmail.com'
EMAIL_HOST_PASSWORD = 'jmmzllnvtesorcyv'
DEFAULT_FROM_EMAIL = 'Sistema de Agendamento <sistemadeagenda5@gmail.com>'
EMAIL_FAIL_SILENTLY = False

# REST + JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKEN': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Localização e idioma
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Redirecionamentos pós login/logout
LOGIN_REDIRECT_URL = '/'
# settings.py
LOGOUT_REDIRECT_URL = '/admin/login/'

# Configs personalizadas
NOME_NEGOCIO = os.getenv('NOME_NEGOCIO', 'Barbearia RD')
EMAIL_REMETENTE = EMAIL_HOST_USER
EMAIL_DESTINO = 'guisantosschutz2@gmail.com'
DOMINIO_SITE = os.getenv('DOMINIO_SITE', 'http://127.0.0.1:8000')
