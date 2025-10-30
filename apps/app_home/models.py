from typing import Iterable, Optional
from django.db import models
import uuid
from apps.app_users.models import Profile
from core.settings.content_path import UserContentPath

class CommonBaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default= uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


MODES = [
    ('public' , 'Public'),
    ('friends' , 'Friends Only'),
    ('only_me' , 'Only Me'),

]


class Posts(CommonBaseModel):
    author = models.ForeignKey( Profile ,on_delete=models.CASCADE)    
    content = models.TextField()
    privacy = models.CharField(max_length=50, choices=MODES, default="public")
    
    def is_liked_by_author(self):
        return Like.objects.filter(post=self, user=self.author).exists()

    
    def __str__(self):
        return f"{self.author}'s Post at {self.created_at}"

class PostImage(CommonBaseModel):
    post = models.ForeignKey(Posts, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to=UserContentPath('post_media', include_date=True))
    transcript = models.TextField(blank=True, null=True)

    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="post_images", null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.author:
            self.author = self.post.author
        super().save(*args, **kwargs)

    @property
    def is_video(self) -> bool:
        name = (self.image.name or '').lower()
        return name.endswith(('.mp4', '.webm', '.ogg', '.mov', '.m4v'))


class Like(CommonBaseModel):
    post = models.ForeignKey(Posts, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="liker_person")


    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} likes post {self.post}"
    

class Comment(CommonBaseModel):
    post = models.ForeignKey(Posts, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user}"

    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('created_at')


class Story(CommonBaseModel):
    author = models.ForeignKey( Profile ,on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to=UserContentPath('stories', include_date=True), blank=True, null=True)
    expires_at = models.DateTimeField()
    privacy = models.CharField(max_length=50, choices=MODES, default="public")
    

    def __str__(self):
        return f"Story by {self.author.user.username}"

class Friends(CommonBaseModel):
    author = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='author')
    friend = models.ManyToManyField(Profile, related_name='friends')
    privacy = models.CharField(max_length=50, choices=MODES, default="public")
    def __str__(self):
        return f"{self.author}'s friends"

class FriendRequests(CommonBaseModel):
    author = models.ForeignKey( Profile,on_delete=models.CASCADE, related_name="person")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")
    
    requested = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)


    def __str__(self):
        return f" {self.sender.first_name} Request to - {self.author.first_name}"


class SavedPost(CommonBaseModel):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} saved {self.post}"