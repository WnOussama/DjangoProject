import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


#  ------ One more parent directory to reach the project root ------>>
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------- COMMON CODE FOR HANDLE MEDA, STATIC and TEMPLATES ---------
TEMPLATE_DIR = os.path.join(BASE_DIR , 'templates')
STATIC_URL = 'static/'
STATIC_DIR = os.path.join(BASE_DIR , 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# -------------=====> EXTRA <=====------------------
AUTH_USER_MODEL = 'app_users.User'
LOGIN_URL = "/auth/login/"
# --------------------========----------------------



SECRET_KEY = os.getenv('SECRET_KEY', 'test-secret-key-12345')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    # ------- Created and 3rd party apps ---------
    'whitenoise.runserver_nostatic',
    'storages',
    'daphne',
    'gunicorn',
    'channels',
    'django_htmx',
    'social_django',

    'apps.app_users',
    'apps.app_chat',
    'apps.app_home',
    'apps.app_account',
    'apps.app_websocket',
    'apps.app_notification',
    # --------- In Built Apps ---------
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
]
ROOT_URLCONF = 'core.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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


#  -========- Django Websocket Setup -==========-

# ASGI_APPLICATION = "core.asgi.application" # your project name

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer", # Or other backend
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)], #  Redis server
#         },
#     },
# }

# WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
# -------------------------------------------------



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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#  --------================ LOAD =============------------

DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576000
FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# -------------=====> ENVIRONMENT VARIABLES <=====------------------
from ..credentials.cloud_storage  import *
from ..credentials.oauth import *
from ..credentials.payment_or_error import *

from .mail_settings import *

# -------------=====> CSRF and CORS <=====------------------
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

CSRF_TRUSTED_ORIGINS = [
    "https://djangoproject-g2cj.onrender.com",
    "http://djangoproject-g2cj.onrender.com",
    "http://44.226.145.213",
    "http://54.187.200.255",
    "http://34.213.214.55",
    "http://35.164.95.156",
    "http://44.230.95.183",
    "http://44.229.200.200",

]

CSRF_TRUSTED_ORIGINS += ["https://*.onrender.com"]
CSRF_TRUSTED_ORIGINS += ["https://*.ngrok-free.app"]
CSRF_TRUSTED_ORIGINS += ["https://*.koyeb.app"]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://djangoproject-g2cj.onrender.com",
    "http://djangoproject-g2cj.onrender.com",
    "https://*.koyeb.app",
    "http://44.226.145.213",
    "http://54.187.200.255",
    "http://34.213.214.55",
    "http://35.164.95.156",
    "http://44.230.95.183",
    "http://44.229.200.200",

]

# -------------=====> LIVE SITE URL <=====------------------
LIVE_SITE_URL_RN=os.getenv('LIVE_SITE_URL_RN', 'http://localhost:8000/')



# ---------- STORAGE SETTINGS -------------
from ..credentials.cloud_storage import *

# MEDIA_DIR = os.path.join(BASE_DIR , 'media')
# MEDIA_URL = '/media/'
# MEDIA_ROOT = MEDIA_DIR
