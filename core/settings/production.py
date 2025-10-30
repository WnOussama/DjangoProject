from .settings import *

# DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')
DEBUG = False

if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')



# ----- in pythonanwhere Using SQLite Database Setup ------------
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

print(f"------>>> DEBUG : {DEBUG} <<<<------")
# ------- MYSQL Database Setup ------------
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#     }
# }


# ----- PostgreSQL Database Setup ------------
# DATABASES = {
#   'default': {
#     'ENGINE': 'django.db.backends.postgresql',
#     'HOST': os.getenv('PGHOST'),
#     'PORT': os.getenv('PGPORT'),
#     'NAME': os.getenv('PGDATABASE'),
#     'USER': os.getenv('PGUSER'),
#     'PASSWORD': os.getenv('PGPASSWORD'),
#     'OPTIONS': {'sslmode': 'require'},
#   }
# }

# import dj_database_url

# DATABASES = {
#     'default': dj_database_url.parse(
#         os.getenv('DATABASE_URL'),
#         conn_max_age=600,
#         ssl_require=True
#     )
# }
db_name = os.getenv('DB_NAME', '')
db_user = os.getenv('DB_USER', '')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', '')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': f'{db_host}',
        'NAME': f'{db_name}',
        'USER': f'{db_user}',
        'PASSWORD': f'{db_password}',
        'OPTIONS': {'sslmode': 'require'},
    }
}

# ============== STORAGE SETTINGS (NOT USING NOW )==============

# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.s3.S3Storage",
#         "OPTIONS": {
#             "access_key": AWS_ACCESS_KEY_ID,
#             "secret_key": AWS_SECRET_ACCESS_KEY,
#             "bucket_name": AWS_STORAGE_BUCKET_NAME,
#             "endpoint_url": AWS_S3_ENDPOINT_URL,
#             "location": AWS_LOCATION,
#             "default_acl": AWS_DEFAULT_ACL,
#             "querystring_auth": False,
#         },
#     },
#     'staticfiles': {
#         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#     }
# }
