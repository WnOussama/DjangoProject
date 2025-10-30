from django.db import models
import uuid
from apps.app_users.models import Profile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class CBS(models.Model):
    uid = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

NOTIFICATION_CATEGORY = (
    ("friend_request", "friend_request"),
    ("message", "message"),
    ("mention", "mention"),
    ("like", "like"),
    ("comment", "comment"),
    ("follow", "follow"),
    ("other", "other")
)

class NoticeCategory(CBS):
    name=models.CharField(max_length=70, choices=NOTIFICATION_CATEGORY, unique=True)
    yes_active=models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name}"

# Sample:
# {
# "person_name": "Ashiq", 
# "person_link": "/profile/ashiq/", 
# "person_profile_picture": "/media/profiles/ashiq.jpg"
# }
class Notification(CBS):
    notice_for=models.ForeignKey( Profile, on_delete=models.CASCADE, related_name="notifications")
    notification=models.CharField(max_length=150)
    
    content = models.JSONField( null=True, blank=True, default=dict)
    link=models.URLField(max_length=500, null=True, blank=True)
    seen = models.BooleanField(default=False)

    category = models.ForeignKey(NoticeCategory,on_delete=models.CASCADE, related_name="notice")

    def __str__(self):
        return self.notification
    


    def save(self, *args, **kwargs):
        if not self.notification:
            raise ValueError("Notification content cannot be empty.")

        # 1) save first so created_at exists
        super().save(*args, **kwargs)

        # 2) build payload
        unseen = Notification.objects.filter(
            notice_for=self.notice_for,
            seen=False
        ).count()

        payload = {
            "count":        unseen,
            "notification": self.notification,
            "link":         self.link,
            "timestamp":    self.created_at.isoformat(),
        }

        # 3) send into the CHANNEL layer
        channel_layer = get_channel_layer()
        group_name    = f"notifications_{self.notice_for.user.uid}"

        async_to_sync(channel_layer.group_send)(
            group_name, {
                # maps to consumer.send_notification
                "type":  "send.notification",     
                "value": json.dumps(payload),
            }
        )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'