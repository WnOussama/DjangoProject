from dotenv import load_dotenv
import os

load_dotenv()



email_backs = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
mail_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
mail_port = int(os.getenv('EMAIL_PORT', 587))
mail_tls = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
email_app_pass = os.getenv('EMAIL_HOST_PASSWORD', '')
mail_user = os.getenv('EMAIL_HOST_USER','')
default_mail_user = os.getenv('DEFAULT_FROM_EMAIL','')


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = f'{email_backs}'
EMAIL_HOST = f'{mail_host}'
EMAIL_PORT = mail_port
EMAIL_USE_TLS = True
EMAIL_HOST_USER = f'{mail_user}'
EMAIL_HOST_PASSWORD = f'{email_app_pass}'
DEFAULT_FROM_EMAIL = f'{default_mail_user}'
# EMAIL_USE_SSL = True