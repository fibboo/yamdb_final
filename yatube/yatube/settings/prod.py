import os

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from yatube.settings import BASE_DIR

env = environ.Env()

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/yatube/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/yatube/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
