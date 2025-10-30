from django.contrib import admin
from .models import ChatGroup,GroupMessage, Message

admin.site.register(ChatGroup)
admin.site.register(GroupMessage)
admin.site.register(Message)
