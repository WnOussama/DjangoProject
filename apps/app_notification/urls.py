from django.urls import path
from .views import NotificationView

urlpatterns = [
    path('list/', NotificationView.as_view(), name='notification_list'),
]
