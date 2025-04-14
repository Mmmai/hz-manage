from celery import shared_task
from django.utils import timezone
from .models import AuditLog

@shared_task
def clean_old_audit_logs(days=30):
    """
    清理超过指定天数的审计日志记录
    """
    threshold_date = timezone.now() - timezone.timedelta(days=days)
    AuditLog.objects.filter(timestamp__lt=threshold_date).delete()