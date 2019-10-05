from .settings import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'teamwork_dh',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': CONFIG['DB_PASSWORD'],
    }
}

sentry_sdk.init(
    dsn="https://5e431d993aca41ebbfbb95d609952527@sentry.io/1515646",
    integrations=[DjangoIntegration()]
)
