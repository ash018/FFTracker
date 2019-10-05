import os
import json
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from corsheaders.defaults import default_methods

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'config.json')) as config_file:
    CONFIG = json.load(config_file)

SECRET_KEY = '64-3)6e$kq&!hgs6pr8*lh&v&3s@jd4)*!nw14(+an8w2-b6la'
DEBUG = True

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_swagger',
    'django_filters',
    'django_extensions',
    'mptt',
    'background_task',
    'apps.user',
    'apps.org',
    'apps.task',
    'apps.location',
    'apps.billing',
    'apps.notification',
    'apps.message',
    'apps.report',
    'apps.support',
    'apps.crm',
    'apps.state',
    'apps.assignment',
    'apps.common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'
AUTH_USER_MODEL = 'user.User'


FB_CONF = CONFIG['FB_CONF']

FB_APP = firebase_admin.initialize_app(credentials.Certificate(FB_CONF))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'teamwork_dh',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': CONFIG['DB_PASSWORD'],
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # filters will define when a logger should run
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },

        # 'special': {
        #     '()': 'project.logging.SpecialFilter',
        #     'foo': 'bar',
        # },
    },

    # format in which logs will be written
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

    # handlers define the file to be written, which level to write in that file,
    # which format to use and which filter applies to that logger
    'handlers': {
        'task_logfile': {
            'level': 'DEBUG',
            # 'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'task_runner', 'task.log'),
            'formatter': 'simple'
        },
        'debug_logfile': {
            'level': 'DEBUG',
            # 'filters': ['require_debug_true'], # do not run debug logger in production
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'simple'
        },
        'error_logfile': {
            'level': 'ERROR',
            # 'filters': ['require_debug_false'], # run logger in production
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'formatter': 'simple'
        },
    },

    # here the handlers for the loggers and the level of each logger is defined
    'loggers': {
        'task_logger': {
            'handlers': ['task_logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'error_logger': {
            'handlers': ['error_logfile'],
            'level': 'ERROR'
         },
        'debug_logger': {
            'handlers': ['debug_logfile'],
            'level': 'DEBUG'
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',

    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=20),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=30),
}


CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    'tw.web.dingi.work',
    'tw.dingi.work',
)

CORS_ORIGIN_REGEX_WHITELIST = (
    'localhost:3000',
    'tw.web.dingi.work',
    'tw.dingi.work',
)

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


SENDER_EMAIL = 'no-reply@dingi.live'
SERVER_EMAIL = SENDER_EMAIL
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-west-2'
AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

AWS_SES_ACCESS_KEY_ID = CONFIG['AWS_SES_ACCESS_KEY_ID']
AWS_SES_SECRET_ACCESS_KEY = CONFIG['AWS_SES_SECRET_ACCESS_KEY']

S3_KEY_ID = CONFIG['S3_KEY_ID']
S3_SECRET_KEY = CONFIG['S3_SECRET_KEY']
S3_BUCKET = CONFIG['S3_BUCKET']


ADMINS = [('Farhad', 'farhad.ahmed@dingi.live'), ]

