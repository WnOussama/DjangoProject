import os
from dotenv import load_dotenv
load_dotenv()


# ---------------- DIGITAL OCEAN SPACES SETTINGS ----------------

# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
# AWS_S3_OBJECT_PARAMETERS = {
#     "CacheControl": "max-age=86400",
# }
# AWS_LOCATION = 'media'
# AWS_DEFAULT_ACL = 'public-read'
# PUBLIC_MEDIA_LOCATION = 'media'
# AWS_QUERYSTRING_AUTH = False
# MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/'


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


# ================ backblazeb S3 SETTINGS ================

DEFAULT_FILE_STORAGE = "core.c_storage.MediaStorage"

AWS_ACCESS_KEY_ID        = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY    = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME  = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = "https://s3.us-east-005.backblazeb2.com"
AWS_S3_REGION_NAME  = "us-east-005"

AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_DEFAULT_ACL = None 
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600
