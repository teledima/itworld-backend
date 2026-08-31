from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from payments.models import Notification, NotificationStatus
from payments.services.notification import send


class Command(BaseCommand):
    help = 'Send notifications job'

    def handle(self, *args, **options):
        success_cnt, failed_cnt = 0, 0
        notifications = Notification.objects.select_related('invoice__project').filter(
            status__in=[NotificationStatus.PENDING, NotificationStatus.FAILED],
        ).only(
            'status',
            'idempotency_key',
            'invoice__status',
            'invoice__updated_at',
            'invoice__project__webhook_url',
            'invoice__project__webhook_secret',
        )

        for notification in notifications.select_for_update(skip_locked=True).iterator(chunk_size=2000):
            try:
                send(notification)
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(tz=timezone.utc)
                success_cnt += 1
            except:
                notification.status = NotificationStatus.FAILED
                failed_cnt += 1
            finally:
                notification.save()

        return f'success: {success_cnt}; failed: {failed_cnt}'
