from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.15.8", "web-production-79ac1.up.railway.app"]

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-79ac1.up.railway.app',
    'https://www.barbearia-rd.com.br',
    'https://barbearia-rd.com.br',
]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
