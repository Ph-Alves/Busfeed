"""
Django settings for busfeed project.

BusFeed - Sistema de transporte público inteligente para Brasília
Configurado seguindo os princípios de Clean Architecture e boas práticas de Django.
"""

from pathlib import Path
from decouple import config
import environ
import dj_database_url

# Configuração de ambiente
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de segurança
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Configurações de aplicação
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',  # Removido temporariamente
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    # 'leaflet',  # Removido temporariamente
    'django_extensions',
    'corsheaders',
]

LOCAL_APPS = [
    'core',
    'users',
    'routes',
    'stops',
    'schedules',
    'notifications',
]

# Apps do BusFeed seguindo arquitetura modular
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware configurado para segurança e performance
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir arquivos estáticos
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Para internacionalização
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug Toolbar para desenvolvimento
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

ROOT_URLCONF = 'busfeed.urls'

# Configuração de templates com Bootstrap 5
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
                'django.template.context_processors.i18n',
                'core.context_processors.app_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'busfeed.wsgi.application'

# Configuração de banco de dados simplificada para desenvolvimento
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',  # Usando SQLite simples
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Para produção com PostgreSQL + PostGIS
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
        )
    }

# Configuração de cache com Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Configuração de sessões com Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8,}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configurações de localização para Brasília
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuração do WhiteNoise para servir arquivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração dos formulários com Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configuração do Leaflet para mapas
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (-15.7801, -47.9292),  # Coordenadas de Brasília
    'DEFAULT_ZOOM': 11,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'SCALE': 'both',
    'ATTRIBUTION_PREFIX': 'BusFeed',
    'TILES': [
        ('OpenStreetMap', 
         'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '© OpenStreetMap contributors'}),
    ],
}

# Configurações do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Configurações de CORS para APIs
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Configurações de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'busfeed.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'busfeed': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Configurações de APIs externas
DFTRANS_API_URL = config('DFTRANS_API_URL', default='')
DFTRANS_API_KEY = config('DFTRANS_API_KEY', default='')

# Configurações de email para notificações
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Configurações de segurança para produção
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações específicas do BusFeed
BUSFEED_SETTINGS = {
    'MAX_SEARCH_RADIUS_KM': 5,
    'DEFAULT_WALKING_SPEED_KMH': 5,
    'CACHE_TIMEOUT_ROUTES': 3600,  # 1 hora
    'CACHE_TIMEOUT_STOPS': 7200,   # 2 horas
    'CACHE_TIMEOUT_SCHEDULES': 300, # 5 minutos
    'REAL_TIME_UPDATE_INTERVAL': 30,  # segundos
    'MAX_ROUTE_ALTERNATIVES': 5,
    'NOTIFICATION_BATCH_SIZE': 100,
}
