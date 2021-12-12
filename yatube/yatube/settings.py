import os

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY_YATUBE', default='YOUR-DJANGO-PROJECT-SECRET-KEY')


INTERNAL_IPS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'posts',
    'users',
    'about',
    'sorl.thumbnail',
    'rest_framework',
    *(['debug_toolbar'] if DEBUG else []),
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG else []),
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yatube.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'yatube.context_processors.year',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'yatube.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/yatube/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/yatube")

MEDIA_URL = '/media/yatube/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/yatube')

# Login

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

if DEBUG is True:
    ALLOWED_HOSTS = [
        '*'
    ]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    ADMINS = [('admin', 'admin@site.com')]

    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')

    # Logging

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'filters': ['require_debug_true'],
            },
        },
        'loggers': {
            'mylogger': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': True,
            },
        },
    }
else:
    sentry_sdk.init(
        dsn=env('SENTRY_DNS', default='you-sentry-dns'),
        integrations=[DjangoIntegration()],
    )

    ALLOWED_HOSTS = [
        '*'
    ]

    DATABASES = {
        'default': {
            'ENGINE': env(
                'DB_ENGINE', default='django.db.backends.postgresql'
            ),
            'NAME': env('DB_NAME_YATUBE', default='postgres_yatube'),
            'USER': env('POSTGRES_USER', default='postgres'),
            'PASSWORD': env('POSTGRES_PASSWORD', default='password'),
            'HOST': env('DB_HOST', default='db'),
            'PORT': env('DB_PORT', default='5432')
        }
    }

    ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS')]

    EMAIL_HOST = env('EMAIL_HOST', default='smtp.example-mail.com')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='you-password')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='username')
    EMAIL_PORT = env('EMAIL_PORT', default=465)
    EMAIL_USE_SSL = env('EMAIL_USE_SSL', default=True)
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='admin@site.com')
