# creating management command to create notification categories
from django.core.management.base import BaseCommand
from apps.app_notification.models import NoticeCategory, NOTIFICATION_CATEGORY
class Command(BaseCommand):
    help = 'Create default notification categories'

    def handle(self, *args, **kwargs):
        for name, _ in NOTIFICATION_CATEGORY:
            if not NoticeCategory.objects.filter(name=name).exists():
                NoticeCategory.objects.create(name=name)
                self.stdout.write(self.style.SUCCESS(f'Successfully created category: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {name}'))
        self.stdout.write(self.style.SUCCESS('All default notification categories checked/created.'))
        