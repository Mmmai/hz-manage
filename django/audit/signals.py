from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog

@receiver(post_save)
def create_audit_log_on_create(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            action='create',
            instance_id=instance.id,
            model_name=sender.__name__,
            changes=str(instance.__dict__)
        )

@receiver(post_save)
def create_audit_log_on_update(sender, instance, **kwargs):
    if not instance._state.adding:  # Check if it's an update
        AuditLog.objects.create(
            action='update',
            instance_id=instance.id,
            model_name=sender.__name__,
            changes=str(instance.__dict__)
        )

@receiver(post_delete)
def create_audit_log_on_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        action='delete',
        instance_id=instance.id,
        model_name=sender.__name__,
        changes=str(instance.__dict__)
    )