from django.utils import timezone
from .models import AuditLog

def create_audit_log(instance, action, user=None):
    """
    Create an audit log entry for the given instance and action.
    
    :param instance: The instance that was modified.
    :param action: The action performed (e.g., 'create', 'update', 'delete').
    :param user: The user who performed the action (optional).
    :return: The created AuditLog instance.
    """
    audit_log = AuditLog(
        instance_id=instance.id,
        action=action,
        user=user,
        timestamp=timezone.now()
    )
    audit_log.save()
    return audit_log

def get_audit_logs(instance_id=None):
    """
    Retrieve audit logs, optionally filtered by instance ID.
    
    :param instance_id: The ID of the instance to filter logs by (optional).
    :return: QuerySet of AuditLog instances.
    """
    if instance_id:
        return AuditLog.objects.filter(instance_id=instance_id).order_by('-timestamp')
    return AuditLog.objects.all().order_by('-timestamp')