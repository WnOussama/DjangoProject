from django.contrib import admin
from . import models as mdl

@admin.register(mdl.NoticeCategory)
class NoticeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'yes_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('yes_active',)
    ordering = ('-created_at',)

@admin.register(mdl.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification', 'notice_for', 'created_at', 'seen', 'category')
    search_fields = ('notification', 'notice_for__user__username')
    list_filter = ('seen', 'category')
    ordering = ('-created_at',)
    raw_id_fields = ('notice_for',)