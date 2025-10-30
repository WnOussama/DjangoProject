from celery import shared_task
from .utils import send_welcome_email

@shared_task
def async_send_welcome(user_id):
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.get(pk=user_id)
    send_welcome_email(user)
