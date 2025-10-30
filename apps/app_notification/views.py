from django.shortcuts import render
from .models import Notification
from django.views import View
# class based view
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# view for make seen of notification or seen all existing unseen notifications
class NotificationView(View):
    def get(self, request):
        notifications = Notification.objects.filter(notice_for=request.user.profile).order_by('-created_at')
        
        notifications.filter(seen=False).update(seen=True)
        
        return render(request, 'notification/notification_list.html', {'notifications': notifications})
    def post(self, request):
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, notice_for=request.user.profile)
                notification.seen = True
                notification.save()
            except Notification.DoesNotExist:
                pass