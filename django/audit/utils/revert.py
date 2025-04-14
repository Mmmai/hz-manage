from django.db import transaction
from audit.models import AuditLog

def revert_audit_log(audit_log_id):
    try:
        with transaction.atomic():
            # Retrieve the audit log entry
            audit_log = AuditLog.objects.get(id=audit_log_id)
            
            # Perform the revert operation based on the action type
            if audit_log.action == 'create':
                # If the action was a creation, delete the instance
                instance = audit_log.instance
                instance.delete()
            elif audit_log.action == 'update':
                # If the action was an update, revert to the previous state
                previous_data = audit_log.previous_data
                instance = audit_log.instance
                for field, value in previous_data.items():
                    setattr(instance, field, value)
                instance.save()
            elif audit_log.action == 'delete':
                # If the action was a deletion, recreate the instance
                instance_data = audit_log.instance_data
                instance = AuditLog.objects.create(**instance_data)
            
            return True
    except AuditLog.DoesNotExist:
        return False
    except Exception as e:
        # Handle any other exceptions that may occur
        return False