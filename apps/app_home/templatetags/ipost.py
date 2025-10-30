from django import template
from apps.app_home.models import Posts, Friends, FriendRequests, Like
from datetime import datetime
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def mypost(inputs):
    try:
        no_of_post = Posts.objects.filter(author=inputs)
    except:
        pass
    if no_of_post:
        return no_of_post.count()
    else:
        return 0

@register.filter
def myfiends(user):
    try:
        no_of_frnd = Friends.objects.get(author=user)
        return no_of_frnd.friend.count()

    except Exception as e:
        print(e)
        return 0

@register.filter
def mefollow(user):
    try:
        no_of_frnd = FriendRequests.objects.filter(sender=user, accepted=False)
        return no_of_frnd.count()

    except Exception as e:
        print(e)
        return 0


@register.filter(name='likers')
def likers(the_post):
    the_reactors = the_post.likes.all()
    
    return [x.user for x in the_reactors]



@register.filter(name="comment_time_fixer")
def comment_time_fixer(time):
    now = timezone.now()
    diff = now - time

    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} sec"
    elif seconds < 3600:
        return f"{seconds//60} min"
    elif seconds < 86400:
        return f"{seconds//3600} hr"
    elif diff.days < 365:
        return f"{diff.days} day"
    else:
        return f"{diff.days//365} yr"
    

@register.filter(name="brief_datetime")
def brief_datetime(value):
    if not value:
        return ""

    dt = timezone.localtime(value)
    date_part = dt.strftime("%y/%m/%d")
    time_part = dt.strftime("%I:%M%p").lstrip("0")
    return f"{date_part}, {time_part}"


@register.filter
def has_liked(post, user_profile):
    """
    Check if a user has liked a post
    Usage: {% if post|has_liked:user.profile %}
    """
    return Like.objects.filter(post=post, user=user_profile).exists()
