from django.db.models import Q, Case, When, IntegerField, F
from django.utils import timezone
from datetime import timedelta
from apps.app_home.models import Posts, Friends
from apps.app_users.models import Profile


def get_newsfeed_posts(profile, limit=20):
    """
    newsfeed algorithm that prioritizes:
    1. User's own posts
    2. Friends' posts
    3. Recent posts
    4. All other posts
    """

    #  user's friends
    existing_friend_object = Friends.objects.filter(author=profile).first()
    friend_profiles = existing_friend_object.friend.all() if existing_friend_object else []
    friend_ids = [friend.uid for friend in friend_profiles]
    
    # priority scoring
    posts = Posts.objects.select_related('author').prefetch_related(
        'images', 'likes', 'comments'
    ).annotate(
        # Priority scoring system
        priority_score=Case(
            # Own posts get highest priority (score: 100)
            When(author=profile, then=100),
            # Friends' posts get high priority (score: 50)
            When(author__uid__in=friend_ids, then=50),
            # Other posts get base priority (score: 10)
            default=10,
            output_field=IntegerField()
        ),
        # Time-based scoring (newer posts get higher scores)
        time_score=Case(
            # Posts from last 24 hours
            When(created_at__gte=timezone.now() - timedelta(hours=24), then=20),
            # Posts from last 7 days
            When(created_at__gte=timezone.now() - timedelta(days=7), then=10),
            # Posts from last 30 days
            When(created_at__gte=timezone.now() - timedelta(days=30), then=5),
            # Older posts
            default=1,
            output_field=IntegerField()
        ),
        # Engagement score (likes + comments)
        engagement_score=F('likes__count') + F('comments__count')
    ).annotate(
        # Final score calculation
        final_score=F('priority_score') + F('time_score') + F('engagement_score')
    ).order_by('-final_score', '-created_at')[:limit]
    
    return posts

# ----------->>  Alternative simpler approach <<-----------
def get_simple_newsfeed_posts(profile):
    """
    Simpler approach using union of querysets
    """
    # user's friends
    existing_friend_object = Friends.objects.filter(author=profile).first()
    friend_profiles = existing_friend_object.friend.all() if existing_friend_object else []
    
    # own posts
    own_posts = Posts.objects.filter(author=profile)
    
    # friends' posts
    friends_posts = Posts.objects.filter(author__in=friend_profiles)
    
    # other posts (excluding own and friends)
    other_posts = Posts.objects.exclude(
        Q(author=profile) | Q(author__in=friend_profiles)
    )
    
    # Combine with priority order
    newsfeed_posts = list(own_posts.order_by('-created_at')[:10]) + \
                    list(friends_posts.order_by('-created_at')[:20]) + \
                    list(other_posts.order_by('-created_at')[:30])
    
    #  final list by creation time
    newsfeed_posts.sort(key=lambda x: x.created_at, reverse=True)
    
    return newsfeed_posts
