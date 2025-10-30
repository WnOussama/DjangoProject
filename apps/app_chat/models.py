from django.db import models
from apps.app_users.models import User
import uuid
from django.utils.text import slugify


class CBM(models.Model):
    uid=models.CharField(max_length=500, unique=True, primary_key=True, editable=False, default=uuid.uuid4)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract=True

class ChatGroup(CBM):
    group_name=models.CharField(max_length=50)
    slug=models.SlugField(editable=False, unique=True)
    room_no = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.room_no:
            last_room = ChatGroup.objects.order_by('room_no').last()
            self.room_no = last_room.room_no + 1 if last_room else 1
            
        if not self.slug:
            slugs = slugify(self.group_name)
            self.slug = slugs+f'-{self.room_no}'
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.group_name}"

class GroupMessage(CBM):
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    group=models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    body=models.TextField()

    class Meta:
        ordering=['created_at']

    def __str__(self) -> str:
        return f"{self.author}'s Message."

class Message(CBM):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False) 
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"
