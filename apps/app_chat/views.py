from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .forms import GroupMessageForm
from django.shortcuts import render, get_object_or_404
from .models import Message
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from apps.app_users.models import User
from apps.app_users.models import Profile
from apps.app_home.models import Friends
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def inbox(request):
    profile = request.user.profile
    existing_friend_object = Friends.objects.filter(author=profile).first()
    friends = existing_friend_object.friend.all() if existing_friend_object else None

    if friends is not None:
        for f in friends:
            f.unread_count = Message.objects.filter(sender=f.user, receiver=request.user, is_read=False).count()

    context = {
        'friends': friends,
    }
    return render(request, "chat/main/messenger.html", context)


@login_required
def chat_room(request, room_name):
    from datetime import datetime, timezone

    search_query = request.GET.get('search', '')
    other_user   = get_object_or_404(User, username=room_name)

    users  = User.objects.exclude(uid=request.user.uid)

    chats  = Message.objects.filter(
        (Q(sender=request.user,   receiver=other_user)) |
        (Q(sender=other_user,     receiver=request.user))
    ).order_by('timestamp')

    # mark messages from other_user to request.user as read
    unread_qs = Message.objects.filter(sender=other_user, receiver=request.user, is_read=False)
    unread_qs.update(is_read=True)

    # after updating, broadcast new unread count
    channel_layer = get_channel_layer()
    total_unread = Message.objects.filter(receiver=request.user, is_read=False).count()
    async_to_sync(channel_layer.group_send)(
        f"messages_{request.user.uid}",
        {
            "type": "send.message_count",
            "value": json.dumps({
                "count": total_unread,
                "sender": other_user.username,
                "sender_unread": 0,
            }),
        }
    )

    if search_query:
        chats = chats.filter(content__icontains=search_query)

    # build last-message helper list
    user_last_messages = []
    for user in users:
        last = Message.objects.filter(
            (Q(sender=request.user, receiver=user)) |
            (Q(sender=user,         receiver=request.user))
        ).order_by('-timestamp').first()

        user_last_messages.append({'user': user, 'last_message': last})

    # --- SAFE SORT ----------------------------------------------------------
    earliest = datetime.min.replace(tzinfo=timezone.utc)
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else earliest,
        reverse=True
    )
    # ------------------------------------------------------------------------

    context = {
        'room_name':  room_name,
        'other_user': other_user,
        'chats': chats,
        'search_query': search_query,
        'user_last_messages': user_last_messages,
    }

    if request.headers.get('Hx-Request'):
        return render(request, 'chat/_conversation.html', context)
    return render(request, 'chat/main/messenger.html', context)


@login_required
def send_message_api(request, room_name):
    if request.method != 'POST':
        return HttpResponse(status=405)

    other_user = get_object_or_404(User, username=room_name)
    text = request.POST.get('message', '').strip()
    if not text:
        return HttpResponse(status=400)

    msg = Message.objects.create(sender=request.user, receiver=other_user, content=text)

    # Return a single message row HTML to append
    return render(request, 'chat/_row.html', {'msg': msg})