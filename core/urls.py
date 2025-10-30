from django.contrib import admin
from django.urls import path, include,re_path

from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('chat/', include("apps.app_chat.urls")),
    path('', include("apps.app_home.urls")),
    path('auth/', include("apps.app_users.urls")),
    path('account/', include("apps.app_account.urls")),
    path('notification/', include("apps.app_notification.urls")),
    path('admin/', admin.site.urls),
    
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

