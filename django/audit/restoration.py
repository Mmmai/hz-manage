import logging
from django.apps import apps
from django.db import transaction, connection
from django.db.models import Max, Q
from rest_framework.exceptions import ValidationError
from .models import AuditLog
from .context import get_audit_context, audit_context
from .registry import registry

logger = logging.getLogger(__name__)

class AuditConflict(Exception):
    pass

class RollbackManager:
    def __init__(self, correlation_id, request=None):
        self.correlation_id = correlation_id
        self.request = request

    def execute(self):
        if not self.correlation_id:
            raise ValidationError("Correlation_id is required for rollback.")
        
        logs_to_process = list(
            AuditLog.objects.filter(
                correlation_id=self.correlation_id,
                action='UPDATE'
            )
            .select_related('content_type')
            .prefetch_related('details')
            .order_by('content_type_id', 'object_id', '-timestamp')
        )
        
        if not logs_to_process:
            raise ValidationError("No update logs found for the given correlation_id.")
        
        # 预检测是否存在更新时间晚于批次中最新更新时间的实例
        latest_timestamps_in_batch = AuditLog.objects.filter(
            correlation_id=self.correlation_id,
            action='UPDATE'
        ).values('content_type_id', 'object_id').annotate(
            latest_ts=Max('timestamp')
        )

        conflict_query = Q()
        for item in latest_timestamps_in_batch:
            conflict_query |= Q(
                content_type_id=item['content_type_id'],
                object_id=item['object_id'],
                timestamp__gt=item['latest_ts']
            )

        if conflict_query and AuditLog.objects.filter(conflict_query).exists():
            raise AuditConflict("Cannot rollback due to newer updates existing for some objects.")
        
        result = {
            'success': [],
            'failure': []
        }
        
        for original_log in reversed(logs_to_process):
            model_class = original_log.content_type.model_class()
            restorer = registry.get_restorer(model_class)
            locker = registry.get_locker(model_class)
            if not restorer or not locker:
                logger.warning(f"No restorer or locker registered for {model_class.__name__}. Skipping.")
                continue
            
            try:
                with transaction.atomic():
                    # 锁定对应实例
                    instance = locker(original_log.object_id, nowait=True)

                    field_details = list(original_log.details.all())
                    snapshot = original_log.changed_fields

                    with audit_context(is_rollback=True, reverted_from=original_log):
                        restorer(
                            instance=instance,
                            snapshot=snapshot,
                            field_details=field_details,
                            request_user=self.request.username
                        )

                result["success"].append(str(original_log.id))

            except ValidationError as exc:
                reason = exc.detail if hasattr(exc, "detail") else str(exc)
                result["failure"].append({"log_id": str(original_log.id), "reason": reason})
            except model_class.DoesNotExist:
                result["failure"].append({"log_id": str(original_log.id), "reason": "Instance does not exist."})
            except Exception as exc:
                logger.exception("Rollback failed for log %s: %s", original_log.id, exc)
                result["failure"].append({"log_id": str(original_log.id), "reason": "An unknown error occurred during rollback."})

        return result